#!/usr/bin/env python3
"""
resolve_section_pages.py - resolve a section number to a physical page range in a PDF.

Usage:
    uv run --with pypdf resolve_section_pages.py <source_pdf> <section_number>

Arguments:
    source_pdf      Absolute path to the source PDF file.
    section_number  Section number in dotted format (e.g. "6.3", "6.3.5").

Output:
    Prints a page range string (e.g. "204-212") to stdout on success.

Exit codes:
    0  success
    1  argument / file / section-not-found error
"""

import os
import re
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

# Matches a body heading like "6.3. Deep Networks" or "6.3 Deep Networks"
# The section number must be followed by a dot/space and then a letter.
BODY_HEADING = re.compile(r"^(\d+(?:\.\d+)+)[.\s]+[A-Za-z]")
SPLIT_HEADING_NUMBER = re.compile(r"^(\d+(?:\.\d+)+)\.?\s*$")

# Matches TOC entries like "6.3 . . . . 204" or
# "6.3 Deep Networks . . . . 186".
TOC_LEADER = re.compile(r"^(\d+(?:\.\d+)+)\s*[\.\s]{3,}")
TOC_ENTRY = re.compile(r"^\s*\d+(?:\.\d+)+\s+.+(?:\.\s*){2,}\d+\s*$")


def next_sibling(section: str) -> str:
    """Return the next sibling section number (e.g. "6.3" → "6.4")."""
    parts = section.split(".")
    parts[-1] = str(int(parts[-1]) + 1)
    return ".".join(parts)


def cache_paths(source_path: str) -> tuple[Path, Path]:
    """Return text and metadata cache paths for a source PDF."""
    digest = hashlib.sha256(os.path.abspath(source_path).encode("utf-8")).hexdigest()
    cache_dir = Path(".cache") / "pdf-text"
    return cache_dir / f"{digest}.txt", cache_dir / f"{digest}.meta.json"


def load_cached_text(source_path: str) -> str | None:
    """Return cached pdftotext output if the PDF metadata still matches."""
    text_path, meta_path = cache_paths(source_path)
    try:
        stat = os.stat(source_path)
        with meta_path.open("r", encoding="utf-8") as f:
            meta = json.load(f)
        if (
            meta.get("source_path") == os.path.abspath(source_path)
            and meta.get("size") == stat.st_size
            and meta.get("mtime") == stat.st_mtime
            and text_path.is_file()
        ):
            return text_path.read_text(encoding="utf-8")
    except (OSError, json.JSONDecodeError):
        return None
    return None


def save_cached_text(source_path: str, text: str) -> None:
    """Best-effort cache write. Cache failures must not fail section resolution."""
    text_path, meta_path = cache_paths(source_path)
    try:
        stat = os.stat(source_path)
        text_path.parent.mkdir(parents=True, exist_ok=True)
        text_path.write_text(text, encoding="utf-8")
        meta = {
            "source_path": os.path.abspath(source_path),
            "size": stat.st_size,
            "mtime": stat.st_mtime,
        }
        meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")
    except OSError as exc:
        print(f"Warning: Could not write pdftotext cache: {exc}", file=sys.stderr)


def read_pdf_text_with_pdftotext(source_path: str) -> str:
    """Read a PDF with pdftotext, using a project-local cache when possible."""
    cached = load_cached_text(source_path)
    if cached is not None:
        return cached

    proc = subprocess.run(
        ["pdftotext", "-layout", source_path, "-"],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    if proc.returncode != 0:
        stderr = proc.stderr.strip()
        raise RuntimeError(stderr or f"pdftotext exited with code {proc.returncode}")

    save_cached_text(source_path, proc.stdout)
    return proc.stdout


def split_pdftotext_pages(text: str) -> list[str]:
    """Split pdftotext output into 1-indexed physical PDF pages."""
    pages = text.split("\f")
    if pages and pages[-1] == "":
        pages.pop()
    return pages


def is_toc_line(line: str) -> bool:
    """Return True for common table-of-contents entries."""
    return bool(TOC_LEADER.match(line) or TOC_ENTRY.match(line))


def line_starts_with_title(line: str) -> bool:
    """Return True when a line looks like the title part of a split heading."""
    return bool(re.match(r"^[A-Za-z]", line.strip()))


def scan_lines_for_headings(page_num: int, lines: list[str]) -> list[tuple[int, str]]:
    """Scan text lines for body section headings."""
    headings: list[tuple[int, str]] = []
    stripped_lines = [line.strip() for line in lines]
    for idx, line in enumerate(stripped_lines):
        m = BODY_HEADING.match(line)
        if m and not is_toc_line(line):
            headings.append((page_num, m.group(1)))
            continue

        # Some PDF text extractors split a heading across lines:
        #   6.3.
        #   Deep Networks
        split_match = SPLIT_HEADING_NUMBER.match(line)
        if not split_match:
            continue
        next_line = next((l for l in stripped_lines[idx + 1 :] if l), "")
        if next_line and line_starts_with_title(next_line) and not is_toc_line(line):
            headings.append((page_num, split_match.group(1)))
    return headings


def scan_text_headings(pages: list[str]) -> list[tuple[int, str]]:
    """Scan pdftotext pages for body section headings."""
    headings: list[tuple[int, str]] = []
    for page_num, text in enumerate(pages, start=1):
        headings.extend(scan_lines_for_headings(page_num, text.splitlines()))
    return headings


def resolve_with_pdftotext(source_path: str, section: str) -> tuple[int, int]:
    """Resolve a section range using pdftotext output."""
    text = read_pdf_text_with_pdftotext(source_path)
    pages = split_pdftotext_pages(text)
    if not pages:
        raise ValueError("pdftotext returned no pages.")
    headings = scan_text_headings(pages)
    return find_section_range(headings, section, len(pages))


def scan_body_headings(reader, target_section: str) -> list[tuple[int, str]]:
    """
    Scan all pages and return a list of (page_1indexed, section_str) tuples
    for lines that look like body headings (not TOC entries).
    """
    headings: list[tuple[int, str]] = []
    for page_num, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        headings.extend(scan_lines_for_headings(page_num, text.splitlines()))
    return headings


def resolve_with_pypdf(source_path: str, section: str) -> tuple[int, int]:
    """Resolve a section range using the slower pypdf fallback."""
    try:
        from pypdf import PdfReader
    except ImportError:
        print(
            "Error: pypdf is not installed. Run with: uv run --with pypdf resolve_section_pages.py",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        reader = PdfReader(source_path)
    except Exception as exc:
        print(f"Error: Could not read PDF: {exc}", file=sys.stderr)
        sys.exit(1)

    total_pages = len(reader.pages)
    headings = scan_body_headings(reader, section)
    return find_section_range(headings, section, total_pages)


def find_section_range(
    headings: list[tuple[int, str]], section: str, total_pages: int
) -> tuple[int, int]:
    """
    Given a list of (page, section_str) tuples, find the physical page range
    for the given section.

    Returns (start_page, end_page) as 1-indexed page numbers.
    """
    sibling = next_sibling(section)

    start_page: int | None = None
    end_page: int | None = None

    for page_num, sec_str in headings:
        if start_page is None:
            if sec_str == section:
                start_page = page_num
        else:
            # Stop at the next sibling section or any ancestor-level section
            # that signals the end of the current section.
            # Strategy: stop when we see a section at the same or shallower depth
            # whose number is >= the next sibling.
            if sec_str == sibling:
                end_page = page_num  # include this page (last sub-section may share it)
                break
            # Also stop at a shallower section (e.g. chapter boundary like "7.")
            target_parts = section.split(".")
            current_parts = sec_str.split(".")
            if len(current_parts) < len(target_parts):
                # Shallower section started — end at the previous page
                end_page = page_num - 1 if page_num > 1 else page_num
                break

    if start_page is None:
        raise ValueError(f"Section '{section}' not found in body text of PDF.")

    if end_page is None:
        end_page = total_pages

    return start_page, end_page


def main() -> None:
    if len(sys.argv) != 3:
        print(
            "Usage: resolve_section_pages.py <source_pdf> <section_number>",
            file=sys.stderr,
        )
        sys.exit(1)

    source_path, section = sys.argv[1], sys.argv[2]

    # Validate section number format
    if not re.fullmatch(r"\d+(\.\d+)+", section):
        print(
            f"Error: Invalid section number format: '{section}'. Expected e.g. '6.3' or '6.3.5'.",
            file=sys.stderr,
        )
        sys.exit(1)

    if not os.path.isfile(source_path):
        print(f"Error: Source PDF not found: {source_path}", file=sys.stderr)
        sys.exit(1)

    try:
        if shutil.which("pdftotext"):
            try:
                start_page, end_page = resolve_with_pdftotext(source_path, section)
            except Exception as exc:
                print(
                    f"Warning: pdftotext failed; falling back to pypdf: {exc}",
                    file=sys.stderr,
                )
                start_page, end_page = resolve_with_pypdf(source_path, section)
        else:
            print("Warning: pdftotext not available; falling back to pypdf", file=sys.stderr)
            start_page, end_page = resolve_with_pypdf(source_path, section)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        print(
            "Hint: Specify physical page numbers directly instead (e.g. '204-212').",
            file=sys.stderr,
        )
        sys.exit(1)

    print(f"{start_page}-{end_page}")


if __name__ == "__main__":
    main()
