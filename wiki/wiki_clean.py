#!/usr/bin/env python3
"""Wiki health-check toolkit — all checks in one place.

Checks: stale pages, duplicate titles, contradiction candidates, compounding
without evidence.

Usage:
    python3 wiki/wiki_clean.py                  # human-readable report
    python3 wiki/wiki_clean.py --json           # machine-readable
    python3 wiki/wiki_clean.py --days 90        # custom staleness threshold
    python3 wiki/wiki_clean.py --threshold 0.7  # stricter duplicate detection
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from datetime import date, datetime
from difflib import SequenceMatcher
from pathlib import Path

WIKI = Path(__file__).resolve().parent
SKIP_FILES = {"index.md", "log.md", "README.md", "_template.md"}
MD_LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+\.md)(?:#[^)]*)?\)")
FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---", re.DOTALL)
DATE_RE = re.compile(r"^last_reviewed\s*:\s*(\d{4}-\d{2}-\d{2})", re.MULTILINE)


def iter_pages() -> list[Path]:
    """All content pages (excludes navigation, templates, scripts)."""
    pages = []
    for p in sorted(WIKI.rglob("*.md")):
        if p.name in SKIP_FILES or p.name.startswith("_template"):
            continue
        pages.append(p)
    return pages


def rel(p: Path) -> str:
    return p.relative_to(WIKI).as_posix()


def page_title(p: Path) -> str:
    """Extract title: first H1 line, or filename slug."""
    try:
        for line in p.read_text(encoding="utf-8", errors="replace").splitlines():
            if line.startswith("# "):
                return line[2:].strip()
    except Exception:
        pass
    return p.stem.replace("_", " ").replace("-", " ")


def page_folder(p: Path) -> str:
    """Return the wiki sub-folder (entities, concepts, etc.)."""
    parts = p.relative_to(WIKI).parts
    return parts[0] if len(parts) > 1 else "root"


def read_text(p: Path) -> str:
    try:
        return p.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return ""


# ─── 0. STALE PAGE DETECTION ───────────────────────────────────────────────

def extract_last_reviewed(path: Path) -> date | None:
    text = path.read_text(encoding="utf-8", errors="replace")
    if not text.startswith("---"):
        return None
    end = text.find("\n---", 3)
    if end == -1:
        return None
    block = text[3:end]
    m = DATE_RE.search(block)
    if not m:
        return None
    try:
        return datetime.strptime(m.group(1), "%Y-%m-%d").date()
    except ValueError:
        return None


def find_stale(threshold_days: int = 180) -> dict:
    """Find pages with outdated or missing last_reviewed front-matter."""
    today = date.today()
    stale: list[dict] = []
    missing: list[str] = []
    fresh = 0
    total = 0
    for path in sorted(WIKI.rglob("*.md")):
        if path.name in SKIP_FILES:
            continue
        total += 1
        reviewed = extract_last_reviewed(path)
        r = path.relative_to(WIKI).as_posix()
        if reviewed is None:
            missing.append(r)
            continue
        age = (today - reviewed).days
        if age > threshold_days:
            stale.append({"path": r, "last_reviewed": reviewed.isoformat(), "age_days": age})
        else:
            fresh += 1
    stale.sort(key=lambda e: -e["age_days"])
    return {
        "today": today.isoformat(),
        "threshold_days": threshold_days,
        "total": total,
        "fresh": fresh,
        "stale_count": len(stale),
        "missing_count": len(missing),
        "stale": stale,
        "missing": sorted(missing),
    }


# ─── 1. DUPLICATE DETECTION ─────────────────────────────────────────────────

def find_duplicates(threshold: float = 0.6) -> list[dict]:
    """Find page pairs with similar titles (potential duplicates/merges).

    Uses SequenceMatcher on normalized titles.  Only compares pages in the
    same wiki sub-folder OR across entity/concept (common mis-filing).
    """
    pages = iter_pages()
    entries = [(p, page_title(p).lower(), page_folder(p)) for p in pages]
    results: list[dict] = []
    seen = set()

    for i, (p1, t1, f1) in enumerate(entries):
        for j, (p2, t2, f2) in enumerate(entries):
            if j <= i:
                continue
            # Compare within same folder, or cross entity↔concept↔pattern
            cross_folders = {"entities", "concepts", "patterns"}
            if f1 != f2 and not (f1 in cross_folders and f2 in cross_folders):
                continue
            ratio = SequenceMatcher(None, t1, t2).ratio()
            if ratio >= threshold:
                key = (min(rel(p1), rel(p2)), max(rel(p1), rel(p2)))
                if key not in seen:
                    seen.add(key)
                    results.append({
                        "page_a": rel(p1),
                        "title_a": page_title(p1),
                        "page_b": rel(p2),
                        "title_b": page_title(p2),
                        "similarity": round(ratio, 2),
                        "same_folder": f1 == f2,
                    })
    results.sort(key=lambda r: -r["similarity"])
    return results


# ─── 2. CONTRADICTION DETECTION ─────────────────────────────────────────────

def extract_outbound_concepts(text: str, page_path: Path) -> set[str]:
    """Extract wiki pages this page links to (normalized to relative paths)."""
    concepts = set()
    for m in MD_LINK_RE.finditer(text):
        link = m.group(2)
        if link.startswith(("http://", "https://", "mailto:")):
            continue
        target = (page_path.parent / link).resolve()
        try:
            concepts.add(target.relative_to(WIKI).as_posix())
        except ValueError:
            pass
    return concepts


def find_contradiction_pairs() -> list[dict]:
    """Group pages by shared outbound links → pairs touching the same concept.

    Two pages that both link to the same concept/entity page may assert
    conflicting things about it.  This outputs the pairs for Claude to review.
    """
    pages = iter_pages()
    # concept_path → list of pages that link to it
    concept_refs: dict[str, list[Path]] = defaultdict(list)

    for p in pages:
        text = read_text(p)
        for c in extract_outbound_concepts(text, p):
            concept_refs[c].append(p)

    # Build pairs: pages that share ≥2 concept links are higher priority
    pair_shared: dict[tuple[str, str], set[str]] = defaultdict(set)
    for concept, referrers in concept_refs.items():
        if len(referrers) < 2:
            continue
        for i, a in enumerate(referrers):
            for b in referrers[i + 1:]:
                key = (min(rel(a), rel(b)), max(rel(a), rel(b)))
                pair_shared[key].add(concept)

    results = []
    for (pa, pb), shared in pair_shared.items():
        results.append({
            "page_a": pa,
            "page_b": pb,
            "shared_concepts": sorted(shared),
            "shared_count": len(shared),
        })
    results.sort(key=lambda r: -r["shared_count"])
    return results


# ─── 3. COMPOUNDING CHECK ───────────────────────────────────────────────────

def extract_sources_section(text: str) -> list[str]:
    """Extract links from the '## Sources' section of a page."""
    sources: list[str] = []
    in_sources = False
    for line in text.splitlines():
        if re.match(r"^##\s+Sources?\b", line, re.IGNORECASE):
            in_sources = True
            continue
        if in_sources and line.startswith("## "):
            break  # next section
        if in_sources:
            for m in MD_LINK_RE.finditer(line):
                sources.append(m.group(2))
            # Also catch bare paths like `raw/transcripts/foo.md`
            bare = re.findall(r"(?:raw/\S+\.(?:md|txt|pdf|html))", line)
            sources.extend(bare)
    return sources


def find_compounding_issues() -> list[dict]:
    """Find pages whose Sources section cites only other wiki pages — no raw evidence.

    A healthy wiki page should ultimately trace back to raw/ sources.
    An insight that only cites other insights is "compounding without evidence".
    """
    pages = iter_pages()
    results: list[dict] = []

    for p in pages:
        text = read_text(p)
        sources = extract_sources_section(text, )
        if not sources:
            continue  # no sources section → handled by other checks

        raw_sources = [s for s in sources if "raw/" in s or s.startswith("http")]
        wiki_sources = [s for s in sources if "raw/" not in s and not s.startswith("http")]

        if wiki_sources and not raw_sources:
            results.append({
                "page": rel(p),
                "title": page_title(p),
                "folder": page_folder(p),
                "wiki_sources_count": len(wiki_sources),
                "wiki_sources": wiki_sources,
                "raw_sources_count": 0,
            })
    results.sort(key=lambda r: -r["wiki_sources_count"])
    return results


# ─── REPORTING ───────────────────────────────────────────────────────────────

def print_stale(report: dict) -> None:
    print(f"  threshold: {report['threshold_days']} days | "
          f"total: {report['total']} | fresh: {report['fresh']} | "
          f"stale: {report['stale_count']} | missing front-matter: {report['missing_count']}")
    if report["stale"]:
        print("\n  🟠 Stale pages (oldest first):")
        for e in report["stale"]:
            print(f"    {e['age_days']:>4}d  {e['last_reviewed']}  {e['path']}")
    if report["missing"]:
        print("\n  ⚠️  Pages without last_reviewed front-matter:")
        for p in report["missing"]:
            print(f"    {p}")


def print_duplicates(dupes: list[dict]) -> None:
    if not dupes:
        print("  No near-duplicate titles found.")
        return
    for d in dupes:
        cross = "" if d["same_folder"] else " [cross-folder]"
        print(f"  {d['similarity']:.0%}  {d['title_a']}  ↔  {d['title_b']}{cross}")
        print(f"       {d['page_a']}  ↔  {d['page_b']}")


def print_contradictions(pairs: list[dict]) -> None:
    if not pairs:
        print("  No overlapping concept pairs found.")
        return
    # Only show top 15 and pairs with ≥2 shared concepts
    shown = [p for p in pairs if p["shared_count"] >= 2][:15]
    if not shown:
        print("  No high-overlap pairs (≥2 shared concepts).")
        return
    for p in shown:
        print(f"  {p['shared_count']} shared  {p['page_a']}  ↔  {p['page_b']}")
        print(f"       concepts: {', '.join(p['shared_concepts'][:5])}")


def print_compounding(issues: list[dict]) -> None:
    if not issues:
        print("  All sourced pages trace back to raw evidence.")
        return
    for c in issues:
        print(f"  ⚠  {c['page']} ({c['wiki_sources_count']} wiki-only sources)")
        for s in c["wiki_sources"][:3]:
            print(f"       └─ {s}")


def run_all(threshold: float, stale_days: int, as_json: bool) -> dict:
    stale_report = find_stale(stale_days)
    dupes = find_duplicates(threshold)
    contras = find_contradiction_pairs()
    compound = find_compounding_issues()

    report = {
        "stale": stale_report,
        "duplicates": dupes,
        "contradiction_pairs": contras,
        "compounding_issues": compound,
        "summary": {
            "stale_count": stale_report["stale_count"],
            "missing_frontmatter_count": stale_report["missing_count"],
            "duplicate_count": len(dupes),
            "contradiction_pair_count": len([c for c in contras if c["shared_count"] >= 2]),
            "compounding_count": len(compound),
        },
    }

    if as_json:
        print(json.dumps(report, indent=2))
    else:
        print("=" * 60)
        print("Wiki Clean — Full Health Check")
        print("=" * 60)
        print(f"\n📅 Stale pages:")
        print_stale(stale_report)
        print(f"\n🔍 Duplicate titles (threshold {threshold:.0%}):")
        print_duplicates(dupes)
        print(f"\n⚡ Contradiction candidates (pages sharing concepts):")
        print_contradictions(contras)
        print(f"\n🔄 Compounding without evidence:")
        print_compounding(compound)
        print()
    return report


def main() -> int:
    ap = argparse.ArgumentParser(description="Wiki health-check toolkit")
    ap.add_argument("--days", type=int, default=180,
                    help="Staleness threshold in days (default 180)")
    ap.add_argument("--threshold", type=float, default=0.6,
                    help="Similarity threshold for duplicate detection (0-1, default 0.6)")
    ap.add_argument("--json", action="store_true", help="JSON output")
    args = ap.parse_args()
    run_all(args.threshold, args.days, args.json)
    return 0


if __name__ == "__main__":
    sys.exit(main())
