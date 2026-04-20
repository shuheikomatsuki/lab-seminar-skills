#!/usr/bin/env python3
"""
extract_pages.py — extract specified pages from a PDF using pypdf.

Usage:
    uv run --with pypdf extract_pages.py <source_pdf> <pages_str> <output_path>

Arguments:
    source_pdf   Absolute path to the source PDF file.
    pages_str    1-indexed page specification. Supported formats:
                   single page : "5"
                   range       : "10-25"
                   list        : "10,12,15"
                   mixed       : "10-15,20-25"
    output_path  Path for the output PDF file.

Exit codes:
    0  success
    1  argument / file / page-range error
"""

import os
import sys


def parse_pages(pages_str: str, total_pages: int) -> list[int]:
    """Parse a 1-indexed page string and return a list of 0-indexed page numbers."""
    page_indices: list[int] = []
    segments = [seg.strip() for seg in pages_str.split(",") if seg.strip()]
    if not segments:
        raise ValueError(f"Empty page specification: '{pages_str}'")

    for seg in segments:
        if "-" in seg:
            parts = seg.split("-")
            if len(parts) != 2 or not parts[0].isdigit() or not parts[1].isdigit():
                raise ValueError(f"Invalid range segment: '{seg}'")
            start, end = int(parts[0]), int(parts[1])
            if start < 1:
                raise ValueError(f"Page numbers are 1-indexed; got start={start}")
            if end < start:
                raise ValueError(f"Range end ({end}) must be >= range start ({start})")
            if end > total_pages:
                raise ValueError(f"Page {end} exceeds document length ({total_pages} pages)")
            page_indices.extend(range(start - 1, end))
        else:
            if not seg.isdigit():
                raise ValueError(f"Non-integer page number: '{seg}'")
            page = int(seg)
            if page < 1:
                raise ValueError(f"Page numbers are 1-indexed; got {page}")
            if page > total_pages:
                raise ValueError(f"Page {page} exceeds document length ({total_pages} pages)")
            page_indices.append(page - 1)

    # Deduplicate while preserving order of first appearance
    seen: set[int] = set()
    deduped: list[int] = []
    for idx in page_indices:
        if idx not in seen:
            seen.add(idx)
            deduped.append(idx)
    return deduped


def main() -> None:
    if len(sys.argv) != 4:
        print("Usage: extract_pages.py <source_pdf> <pages_str> <output_path>", file=sys.stderr)
        sys.exit(1)

    source_path, pages_str, output_path = sys.argv[1], sys.argv[2], sys.argv[3]

    try:
        from pypdf import PdfReader, PdfWriter
    except ImportError:
        print("Error: pypdf is not installed. Run with: uv run --with pypdf extract_pages.py", file=sys.stderr)
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

    try:
        page_indices = parse_pages(pages_str, total_pages)
    except ValueError as exc:
        print(f"Error: Invalid page specification — {exc}", file=sys.stderr)
        sys.exit(1)

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

    writer = PdfWriter()
    for idx in page_indices:
        writer.add_page(reader.pages[idx])

    try:
        with open(output_path, "wb") as f:
            writer.write(f)
    except OSError as exc:
        print(f"Error: Could not write output PDF: {exc}", file=sys.stderr)
        sys.exit(1)

    print(f"OK: Extracted {len(page_indices)} page(s) from '{source_path}' → '{output_path}'")


if __name__ == "__main__":
    main()
