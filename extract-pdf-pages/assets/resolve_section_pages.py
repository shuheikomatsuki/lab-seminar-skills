#!/usr/bin/env python3
"""
resolve_section_pages.py — resolve a section number to a physical page range in a PDF.

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
import sys

# Matches a body heading like "6.3. Deep Networks" or "6.3 Deep Networks"
# The section number must be followed by a dot/space and then a letter.
BODY_HEADING = re.compile(r"^(\d+(?:\.\d+)+)[.\s]+[A-Za-z]")

# Matches a TOC entry like "6.3 . . . . 204" (dot leader or trailing digits)
TOC_LEADER = re.compile(r"^(\d+(?:\.\d+)+)\s*[\.\s]{3,}")


def next_sibling(section: str) -> str:
    """Return the next sibling section number (e.g. "6.3" → "6.4")."""
    parts = section.split(".")
    parts[-1] = str(int(parts[-1]) + 1)
    return ".".join(parts)


def scan_body_headings(reader, target_section: str) -> list[tuple[int, str]]:
    """
    Scan all pages and return a list of (page_1indexed, section_str) tuples
    for lines that look like body headings (not TOC entries).
    """
    headings: list[tuple[int, str]] = []
    for page_num, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        for line in text.splitlines():
            line = line.strip()
            m = BODY_HEADING.match(line)
            if not m:
                continue
            # Exclude TOC entries (dot leaders)
            if TOC_LEADER.match(line):
                continue
            headings.append((page_num, m.group(1)))
    return headings


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

    try:
        from pypdf import PdfReader
    except ImportError:
        print(
            "Error: pypdf is not installed. Run with: uv run --with pypdf resolve_section_pages.py",
            file=sys.stderr,
        )
        sys.exit(1)

    if not os.path.isfile(source_path):
        print(f"Error: Source PDF not found: {source_path}", file=sys.stderr)
        sys.exit(1)

    try:
        reader = PdfReader(source_path)
    except Exception as exc:
        print(f"Error: Could not read PDF: {exc}", file=sys.stderr)
        sys.exit(1)

    total_pages = len(reader.pages)
    headings = scan_body_headings(reader, section)

    try:
        start_page, end_page = find_section_range(headings, section, total_pages)
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
