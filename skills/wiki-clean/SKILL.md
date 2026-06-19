---
name: wiki-clean
description: >
  Run a health check on the personal wiki following the Karpathy LLM Wiki pattern.
  Detects contradictions between pages, stale claims, orphan pages without inbound links,
  concepts mentioned but missing their own page, and cross-reference gaps.
  Use this skill whenever the user says "clean the wiki", "wiki health check", "check my wiki",
  "are there gaps in the wiki", "what's missing in the wiki", "wiki audit", "wiki cleanup",
  or any variation asking about wiki quality, consistency, or completeness.
  Also trigger when the user asks "what should I ingest next" or "where are the gaps" —
  these are cleanup questions even if the user doesn't use the word "clean".
  Can be scheduled to run weekly for proactive maintenance.
---

# Wiki Clean — Health Check

You are running a health check on the user's personal wiki. The wiki follows the Karpathy LLM Wiki pattern: raw sources in `raw/`, interlinked markdown pages in `wiki/`, and conventions in `CLAUDE.md`.

The purpose of cleaning is to keep the wiki **compounding** — a wiki with broken links, orphan pages, and missing concepts loses its main advantage over simple RAG. Think of yourself as a librarian doing a periodic audit of the catalogue.

## Architecture reminder

```
<root>/
├── raw/                    # Immutable sources
│   ├── articles/
│   ├── transcripts/
│   ├── specs/
│   └── screenshots/
├── wiki/
│   ├── index.md            # Catalogue — the entry point
│   ├── log.md              # Chronological operation log
│   ├── backlinks.py        # Reverse-graph generator — clean runs this first
│   ├── wiki_clean.py       # Health-check toolkit (stale, duplicates, contradictions, compounding)
│   ├── entities/           # People, companies, products, squads
│   ├── concepts/           # Technical/business concepts (definitional, stable)
│   ├── patterns/           # Observed signals & behaviors (interpretive, rankable)
│   ├── syntheses/          # Cross-source analyses, meeting summaries
│   └── mocs/               # Maps of Content
└── CLAUDE.md               # Schema & conventions
```

## The clean workflow

Cleaning is a **four-phase** process: refresh the graph, scan, report, then fix (with user approval).

### Phase 0 — Refresh the graph (AUTOMATED)

Before analyzing anything, **run `python3 wiki/backlinks.py`**. This regenerates the `<!-- BACKLINKS:START -->` block on every page, which is the authoritative source of truth for inbound-link analysis. Skipping this step means orphan detection and cross-reference gap detection run on stale data.

Report the output briefly (e.g., "Refreshed backlinks on N pages") and move to Phase 1.

### Phase 0b — Run advanced clean checks (AUTOMATED)

After refreshing backlinks, **run `python3 wiki/wiki_clean.py --json`**. This produces machine-readable results for all structural checks:

- 🔍 **Duplicates** — pages with similar titles (potential merge candidates). Adjust threshold with `--threshold 0.7` for stricter matching.
- ⚡ **Contradiction candidates** — page pairs that link to ≥2 of the same concepts. These are the pairs where you should actually **read both pages and compare claims** in Phase 1. Don't just list them — look for real conflicts.
- 🔄 **Compounding without evidence** — pages whose Sources section only cites other wiki pages, never `raw/` files. An insight that only cites other insights is building on sand. Flag these for the user to ground with a real source.

Parse the JSON output and carry these findings into Phase 2 reporting.

### Phase 1 — Scan (AUTOMATED)

Read the full wiki systematically. This is where you gather all the data before drawing conclusions.

1. **Read `wiki/index.md`** to get the catalogue of all pages.

2. **Read every wiki page** listed in the index. For each page, extract:
   - All outbound markdown links (both `[text](path)` and inline mentions of concepts/entities)
   - The `## Referenced by` block (auto-maintained by `backlinks.py`) — this gives you the inbound link count for free
   - The "Sources" section — which raw files does this page cite?
   - Key claims, dates, and status markers (e.g., "H2 2026", "WIP", "en cours")
   - The last time the page was updated (from `wiki/log.md`)

3. **Read `wiki/log.md`** to build a timeline of operations and know when each page was last touched.

4. **Scan `raw/`** to find sources that exist but may not have been ingested yet (no corresponding wiki page or log entry).

5. **Scan `CLAUDE.md`** glossary and team roster for concepts/entities that should have wiki pages but don't.

6. **Build a link graph**: use the `## Referenced by` blocks (inbound) plus your scan of markdown links (outbound). Orphans = pages with empty or missing backlinks block. Hubs = pages with >10 inbound links.

### Phase 2 — Report (INTERACTIVE)

Present findings to the user as a structured clean report. Organize by severity — the user should be able to scan quickly and decide what to act on.

Structure the report as follows:

#### 🔴 Contradictions
Pages that assert conflicting facts. Use the contradiction-candidate pairs from `wiki_clean.py` as your starting point: for each high-overlap pair, **read both pages and compare claims**. Quote the contradicting passages with page links. This is the highest priority because contradictions actively mislead.

#### 🔴 Duplicate / near-duplicate pages
Pages with highly similar titles flagged by `wiki_clean.py duplicates`. For each pair, check whether they genuinely cover the same topic and recommend: **merge** (pick the richer one, redirect), **rename** (titles are similar but topics differ), or **keep** (false positive).

#### 🟠 Compounding without evidence
Pages whose Sources section only cites other wiki pages — no `raw/` files, no external URLs. These are insights built on insights with no grounding in primary evidence. For each one, recommend which raw source should be added, or whether the page should be demoted to a stub until evidence is ingested.

#### 🟠 Stale content
Pages with dates or status markers that are likely outdated given the current date or newer sources. For example, a page saying "planned for Q1 2026" when we're in Q2 2026 — is this still planned, done, or abandoned?

#### 🟡 Orphan pages
Pages whose `## Referenced by` block is empty or missing. They exist in the index but nothing points to them — they're invisible in practice. These need either cross-references from other pages or deletion if they're no longer relevant.

#### 🟡 Pattern hygiene
Pattern-specific checks:
- Patterns with only 1 source → flag as "proto-pattern" (should live in synthesis, not patterns/)
- Patterns with stale confidence (source_count doesn't match actual evidence rows)
- Patterns in `concepts/` that should be in `patterns/` (interpretive claims disguised as definitions)
- Contradicting patterns without cross-references in their "Contradictions" section

#### 🟡 Missing pages
Concepts, entities, patterns, or terms that are mentioned across multiple wiki pages but don't have their own dedicated page. Also check the CLAUDE.md glossary — if a concept appears there (e.g., EBICS, pain.001, e-invoicing) but has no `wiki/concepts/` page, flag it. Prioritize by frequency of mention.

#### 🔵 Broken or missing links
Markdown links that point to non-existent files, or pages that reference each other conceptually but don't have explicit links.

#### 🔵 Un-ingested sources
Files in `raw/` that don't appear in any wiki page's "Sources" section and have no corresponding log entry. These are sources that were saved but never processed.

#### 💡 Suggestions
Proactive ideas to strengthen the wiki:
- New sources worth ingesting (based on gaps you spotted)
- Pages that would benefit from merging or splitting
- Categories in the index that could be reorganized
- Areas where the wiki has depth vs. areas where it's thin

**Keep the report concise.** Use tables where it helps scanning. Don't write paragraphs where a bullet with a link suffices.

At the end of the report, ask the user which items they want to fix now.

### Phase 3 — Propose fixes (REVIEW MODE)

**Do NOT apply any changes yet.** Present a clear list of proposed fixes so the user can review and approve each one. This is important — the user wants to understand what will change before anything is modified.

For each proposed fix, show:
- 📄 **Which file** will be modified or created
- ✏️ **What changes** — a short description of what you'll add, update, or link
- 🎯 **Why** — which clean finding this addresses

Group the proposed fixes by type:

1. **Cross-references to add** — list each `[text](path)` link you'd insert and in which file
2. **Stale content to update** — show the current claim and what you'd replace it with (and your source)
3. **Missing pages to create** — show the proposed filename and a 1-line summary of what the page would contain
4. **Broken links to fix** — show the broken path and the corrected one
5. **Index updates** — new entries you'd add to `wiki/index.md`

End with: **"Which of these should I apply? You can say 'all', pick by number, or skip any."**

### Phase 4 — Apply approved fixes

Only after the user explicitly approves (all or specific items):

1. Apply the approved changes
2. **Update `wiki/index.md`** — add any new pages, fix descriptions if they've drifted
3. **Re-run `python3 wiki/backlinks.py`** — so the reverse graph reflects any new links or pages
4. **Append to `wiki/log.md`**:
   - Format: `## [YYYY-MM-DD] clean | Wiki health check`
   - List: issues found, fixes applied, items deferred
   - Append-only — never modify existing log entries
5. **Summarize** what was done and what was skipped/deferred

## Guidelines

- **Non-destructive by default**: cleaning should never delete content without explicit user approval. When in doubt, flag rather than fix.
- **Language**: all wiki content (report output written into wiki pages, any new pages created) must be in **English**, per the project's `CLAUDE.md`. Raw sources stay in their original language. The conversation with the user can be in whatever language they use.
- **Cross-links are king**: the single most valuable thing cleaning does is densify the link graph. Every fix should consider "what else should this page link to?"
- **Don't invent information**: if a concept needs a page but you don't have enough context, create a stub page and note that it needs a source ingested. Don't fill pages with generic information — the wiki should be grounded in actual sources.
- **Don't hand-maintain backlinks**: the `## Referenced by` block is auto-generated. Never edit it manually. If it looks wrong, rerun `backlinks.py` (check for broken link syntax in the source page).
- **Quantify the health**: at the top of your report, give a quick health summary — total pages, total links, orphan count, coverage of CLAUDE.md glossary terms. This helps the user track improvement over time.
