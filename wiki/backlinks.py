#!/usr/bin/env python3
"""
Backlinks generator for the LLM wiki.

Scans every .md file under wiki/ for markdown links to other wiki .md files,
builds a reverse index, and writes/updates a `## Referenced by` block at the
bottom of each target page.

Idempotent: re-running replaces the existing block.
"""
import os
import re
from pathlib import Path
from collections import defaultdict

WIKI = Path(__file__).resolve().parent
# Files that should NOT get a "Referenced by" block (they are navigation, not content)
EXCLUDE_TARGETS = {"index.md", "log.md"}
# Folders to skip entirely as sources (we don't care who they reference)
EXCLUDE_SOURCES = {"log.md"}  # index.md is allowed as a source


def is_template(name: str) -> bool:
    """Template files start with `_template` — they are scaffolding, not content."""
    return name.startswith("_template")

MD_LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+\.md)(?:#[^)]*)?\)")
BACKLINKS_MARKER = "<!-- BACKLINKS:START -->"
BACKLINKS_END = "<!-- BACKLINKS:END -->"


def iter_md_files(root: Path):
    for path in root.rglob("*.md"):
        yield path


def strip_existing_backlinks(content: str) -> str:
    pattern = re.compile(
        re.escape(BACKLINKS_MARKER) + r".*?" + re.escape(BACKLINKS_END) + r"\n?",
        re.DOTALL,
    )
    cleaned = pattern.sub("", content)
    # also trim trailing whitespace AND any trailing `---` separators
    # (otherwise re-running accumulates one `---` per run, since
    # apply_backlinks prepends a fresh `---` separator each time).
    cleaned = cleaned.rstrip()
    while cleaned.endswith("---"):
        cleaned = cleaned[:-3].rstrip()
    return cleaned + "\n"


def build_reverse_index():
    reverse = defaultdict(set)  # target_abs_path -> set of source_abs_paths
    for src in iter_md_files(WIKI):
        if src.name in EXCLUDE_SOURCES or is_template(src.name):
            continue
        try:
            text = src.read_text(encoding="utf-8")
        except Exception:
            continue
        # Strip existing backlinks block BEFORE scanning so backlink links
        # themselves don't register as references.
        text_for_scan = strip_existing_backlinks(text)
        for match in MD_LINK_RE.finditer(text_for_scan):
            link = match.group(2)
            if link.startswith(("http://", "https://", "mailto:")):
                continue
            # resolve relative to src's directory
            target = (src.parent / link).resolve()
            if not str(target).startswith(str(WIKI.resolve())):
                continue
            if target == src.resolve():
                continue
            reverse[target].add(src.resolve())
    return reverse


def format_backlinks_section(target: Path, sources: set) -> str:
    # Group by folder for readability
    by_group = defaultdict(list)
    for src in sorted(sources):
        rel = src.relative_to(WIKI)
        group = rel.parts[0] if len(rel.parts) > 1 else "root"
        # Compute link relative to target's directory
        link_rel = os.path.relpath(src, target.parent)
        # Title = first H1 if available, else filename
        try:
            first_line = src.read_text(encoding="utf-8").splitlines()[0]
            if first_line.startswith("# "):
                title = first_line[2:].strip()
            else:
                title = src.stem.replace("_", " ")
        except Exception:
            title = src.stem.replace("_", " ")
        by_group[group].append((title, link_rel))

    lines = [BACKLINKS_MARKER, "## Referenced by", ""]
    group_order = ["entities", "concepts", "patterns", "syntheses", "root"]
    for group in group_order:
        if group not in by_group:
            continue
        label = group.capitalize() if group != "root" else "Other"
        lines.append(f"**{label}**")
        lines.append("")
        for title, link in sorted(by_group[group]):
            lines.append(f"- [{title}]({link})")
        lines.append("")
    # Catch any groups not in the canonical order
    for group, items in by_group.items():
        if group in group_order:
            continue
        lines.append(f"**{group.capitalize()}**")
        lines.append("")
        for title, link in sorted(items):
            lines.append(f"- [{title}]({link})")
        lines.append("")
    lines.append(BACKLINKS_END)
    return "\n".join(lines) + "\n"


def apply_backlinks(reverse: dict) -> tuple[int, int]:
    updated = 0
    cleared = 0
    for target in iter_md_files(WIKI):
        if target.name in EXCLUDE_TARGETS or is_template(target.name):
            continue
        content = target.read_text(encoding="utf-8")
        cleaned = strip_existing_backlinks(content)
        sources = reverse.get(target.resolve(), set())
        if not sources:
            if cleaned != content:
                target.write_text(cleaned, encoding="utf-8")
                cleared += 1
            continue
        block = format_backlinks_section(target, sources)
        new_content = cleaned.rstrip() + "\n\n---\n\n" + block
        if new_content != content:
            target.write_text(new_content, encoding="utf-8")
            updated += 1
    return updated, cleared


def main():
    print(f"Scanning {WIKI}")
    reverse = build_reverse_index()
    print(f"Found backlinks for {len(reverse)} target pages")
    updated, cleared = apply_backlinks(reverse)
    print(f"Updated {updated} pages")
    print(f"Cleared stale blocks from {cleared} pages")


if __name__ == "__main__":
    main()
