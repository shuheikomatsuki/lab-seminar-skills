#!/usr/bin/env python3
"""Replace image-slot comments with Markdown image links for generated images."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


SLOT_RE_TEMPLATE = r"<!--\s*image-slot:\s*{image_id}\s*-->"


def load_entries(prompts_path: Path) -> list[dict]:
    """Parse the small image_prompts.yml schema without external dependencies."""

    lines = prompts_path.read_text(encoding="utf-8").splitlines()
    if any(line.strip() == "images: []" for line in lines):
        return []
    if not any(line.strip() == "images:" for line in lines):
        raise ValueError("image_prompts.yml must contain a top-level 'images' key")

    entries: list[dict] = []
    current: dict | None = None
    in_images = False
    in_block = False
    block_indent = 0

    for raw_line in lines:
        stripped = raw_line.strip()

        if not stripped or stripped.startswith("#"):
            continue

        if stripped == "images:":
            in_images = True
            continue

        if not in_images:
            continue

        indent = len(raw_line) - len(raw_line.lstrip(" "))

        if in_block:
            if indent > block_indent:
                continue
            in_block = False

        if stripped.startswith("- "):
            if current is not None:
                entries.append(current)
            current = {}
            rest = stripped[2:].strip()
            if rest:
                key, value = parse_key_value(rest)
                current[key] = value
                if value == "|":
                    in_block = True
                    block_indent = indent
            continue

        if current is None:
            if stripped == "[]":
                return []
            continue

        if ":" not in stripped:
            continue

        key, value = parse_key_value(stripped)
        current[key] = value
        if value == "|":
            in_block = True
            block_indent = indent

    if current is not None:
        entries.append(current)

    return entries


def parse_key_value(text: str) -> tuple[str, str]:
    key, value = text.split(":", 1)
    return key.strip(), unquote(value.strip())


def unquote(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value


def as_session_relative(path_value: str, field: str) -> Path:
    path = Path(path_value)
    if path.is_absolute() or ".." in path.parts:
        raise ValueError(f"{field} must be a session-relative path: {path_value}")
    return path


def replace_slots(session_dir: Path, entries: list[dict], dry_run: bool) -> int:
    replaced: list[str] = []
    missing_images: list[str] = []
    missing_articles: list[str] = []
    missing_slots: list[str] = []
    skipped: list[str] = []

    changed_files: dict[Path, str] = {}

    for entry in entries:
        image_id = str(entry.get("id", "")).strip()
        article_value = str(entry.get("article", "")).strip()
        filename_value = str(entry.get("filename", "")).strip()
        alt = str(entry.get("alt", "")).strip()

        if not image_id or not article_value or not filename_value:
            skipped.append(f"{image_id or '(missing id)'}: id/article/filename is required")
            continue

        article_rel = as_session_relative(article_value, "article")
        image_rel = as_session_relative(filename_value, "filename")
        article_path = session_dir / article_rel
        image_path = session_dir / image_rel

        if not article_path.is_file():
            missing_articles.append(f"{image_id}: {article_rel}")
            continue

        if not image_path.is_file():
            missing_images.append(f"{image_id}: {image_rel}")
            continue

        text = changed_files.get(article_path)
        if text is None:
            text = article_path.read_text(encoding="utf-8")

        slot_re = re.compile(SLOT_RE_TEMPLATE.format(image_id=re.escape(image_id)))
        markdown_image = f"![{alt or image_id}]({image_rel.as_posix()})"

        if not slot_re.search(text):
            if markdown_image in text:
                skipped.append(f"{image_id}: already embedded in {article_rel}")
            else:
                missing_slots.append(f"{image_id}: {article_rel}")
            continue

        new_text, count = slot_re.subn(markdown_image, text, count=1)
        changed_files[article_path] = new_text
        action = "would replace" if dry_run else "replaced"
        replaced.append(f"{action}: {article_rel} :: {image_id} -> {image_rel}")

    if not dry_run:
        for article_path, text in changed_files.items():
            article_path.write_text(text, encoding="utf-8")

    print("Replacements:")
    if replaced:
        for line in replaced:
            print(f"  - {line}")
    else:
        print("  none")

    print("Missing generated images:")
    if missing_images:
        for line in missing_images:
            print(f"  - {line}")
    else:
        print("  none")

    if missing_articles:
        print("Missing articles:")
        for line in missing_articles:
            print(f"  - {line}")

    if missing_slots:
        print("Missing slots:")
        for line in missing_slots:
            print(f"  - {line}")

    if skipped:
        print("Skipped:")
        for line in skipped:
            print(f"  - {line}")

    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("session_dir", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    session_dir = args.session_dir
    prompts_path = session_dir / "image_prompts.yml"

    if not session_dir.is_dir():
        print(f"Error: session directory not found: {session_dir}", file=sys.stderr)
        return 1
    if not prompts_path.is_file():
        print(f"Error: image_prompts.yml not found: {prompts_path}", file=sys.stderr)
        return 1

    try:
        entries = load_entries(prompts_path)
        return replace_slots(session_dir, entries, args.dry_run)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
