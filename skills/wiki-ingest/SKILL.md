---
name: wiki-ingest
description: "Ingest a new source into the personal wiki following the Karpathy LLM Wiki pattern. Use this skill whenever the user shares a transcript, article, Slack thread, Notion page, or any other source material and wants it processed into their knowledge base. Trigger on phrases like \"ingest this\", \"process this\", \"add this to the wiki\", \"here's a transcript\", \"here's an article\", or when the user pastes/uploads raw content that should be captured. Also trigger when the user says \"I had a call with...\", \"I read this article about...\", \"check this Slack thread\", or shares a URL to a Notion page. Even if the user doesn't explicitly say \"ingest\", if they share substantial content (transcript, article, thread) in the context of their work, suggest using this skill."
---

# Wiki Ingest

You are processing a new source into the user's personal wiki. The wiki follows the Karpathy LLM Wiki pattern: raw sources are stored immutably, and a wiki layer of interlinked markdown pages is maintained by the LLM.

## ⚠️ Core principle — NEVER rebuild, ALWAYS incrementally update

The wiki already exists on disk. Your job is to **add to it**, not to recreate it. Before writing anything:
- Always inspect the actual filesystem state (not just the index)
- Always prefer `Edit` (append/update) over `Write` (which overwrites) for any file that already exists
- Never rewrite `wiki/index.md` from scratch — only insert new rows into existing tables
- Never delete existing content unless explicitly contradicted by a newer source

If at any point you feel tempted to "regenerate" or "rebuild" a wiki file — stop. You must `Read` it first and `Edit` it.

## Architecture reminder

```
<root>/
├── raw/                    # Immutable sources — never modify after saving
│   ├── articles/
│   ├── transcripts/
│   ├── specs/
│   └── screenshots/
├── wiki/
│   ├── index.md            # Catalogue of all wiki pages — read this FIRST
│   ├── log.md              # Chronological append-only log of operations
│   ├── entities/           # People, companies, products, squads
│   ├── concepts/           # Technical/business concepts (definitional, stable)
│   ├── patterns/           # Observed signals & behaviors (interpretive, rankable)
│   ├── syntheses/          # Cross-source analyses, meeting summaries, saved queries
│   └── mocs/               # Maps of Content — thematic navigation
```

## The ingest workflow

Ingesting is a **two-phase** process: first you discuss with the user, then you write.

### Phase 1 — Read & Discuss (INTERACTIVE)

This phase is about making sure you understood the source correctly before writing anything permanent. Do not skip it.

1. **Identify the source type** and save the raw content:
   - **Transcript** → `raw/transcripts/YYYY-MM-DD_<short_title>.md`
   - **Article** → `raw/articles/YYYY-MM-DD_<short_title>.md`
   - **Slack thread** → use the Slack MCP to read the thread, then save to `raw/articles/YYYY-MM-DD_<short_title>.md`
   - **Notion page** → use the Notion MCP to fetch the page, then save to `raw/articles/YYYY-MM-DD_<short_title>.md`
   - If the user pastes text directly in the conversation, infer the type from context.

   ⚠️ **Save the source verbatim — no edits of any kind.** Do not rephrase, summarize, translate, reorganize, deduplicate, fix typos, or adjust formatting (even minor cleanup like line breaks, whitespace, or stripping export chrome). The file in `raw/` must match exactly what the user shared or what the MCP returned. All synthesis and cleanup happens in `wiki/`, never in `raw/`. When in doubt, save as-is.
   - Before saving, check if a file with the same target path already exists (Glob or ls). If it does, ask the user whether to overwrite or pick a new slug.

2. **Inspect the actual wiki state** — do NOT rely only on `wiki/index.md`, it may be out of sync with the filesystem. Do all four:
   - Read `wiki/index.md` for the catalog overview
   - **List the actual files** on disk: `ls wiki/entities/`, `ls wiki/concepts/`, `ls wiki/syntheses/`, `ls wiki/mocs/` (use Bash or the Glob tool)
   - If a file exists on disk but is missing from the index, the **file is the source of truth**. Flag the gap and plan to patch the index during the update step.

3. **Present takeaways** to the user. This is the most important step — it's where the user validates your understanding before you write wiki pages. Structure your takeaways as:
   - A short **summary** (2-3 lines max) of what the source is about
   - **Key points** as a bulleted list — decisions, facts, insights, open questions
   - **Entities spotted** — people, companies, products mentioned (flag which are NEW vs. already-existing-on-disk)
   - **Concepts touched** — technical or business concepts, i.e. definitions and standards (flag NEW vs. existing-on-disk)
   - **Patterns spotted** — recurring behaviors, objections, signals, failure modes observed in the source. A pattern needs ≥2 sources to be created as its own page; if this is the first occurrence, note it as a "proto-pattern" that will live in the synthesis until confirmed. Flag NEW vs. existing-on-disk patterns
   - **Connections** — how this source relates to existing wiki pages (cite the actual file paths)
   - **MOCs** — which existing MOCs in `wiki/mocs/` this source feeds into, and whether the source is thematically broad enough to warrant a **new MOC** (flag it if so, don't create one unilaterally)

   Keep it concise. The user wants to scan and confirm, not read an essay.

4. **Wait for the user's OK** before proceeding to Phase 2. They might correct your understanding, add context, or tell you to emphasize different aspects. Incorporate their feedback.

### Phase 2 — Write (AUTOMATED, but incremental)

Once the user confirms, write all wiki pages in a single pass. The goal is to be thorough: one source typically touches 5-15 wiki pages. **But every write must be incremental.**

**🕒 Staleness front-matter — MANDATORY on every page write:**
- **New pages** must start with:
  ```
  ---
  last_reviewed: YYYY-MM-DD
  ---
  ```
  where the date is today.
- **Existing pages** being edited must have their `last_reviewed:` field bumped to today's date (inside the existing front-matter block). If a page somehow lacks a front-matter block, add one.
- Skip only `index.md`, `log.md`, `README.md`, `_template.md`.


1. **Create a synthesis page** in `wiki/syntheses/` (this one is almost always new):
   - Filename: `YYYY-MM-DD_<descriptive_slug>.md`
   - Before writing, Glob/ls to confirm no file with that name exists. If one does, bump the slug or ask the user.
   - Include: context, key points structured by theme, decisions & next steps (if applicable), links to entity/concept pages
   - Always link back to the raw source with a relative path
   - For meetings: include a participants line and a decisions/actions table

2. **Create or update MOC pages** in `wiki/mocs/` — same Read-before-Write pattern:
   - For each MOC this source touches, `Read` the file first, then `Edit` to add links in the relevant sections: new synthesis under 📚, new entities under 👥, new concepts under 🧠, open questions under ❓
   - If a **new MOC** was agreed on in Phase 1, use `wiki/mocs/_template.md` as the starting structure and `Write` a new `MOC_<Topic>.md`. Link to all relevant existing wiki pages from the start — a MOC is only useful if it's well-connected.
   - MOCs are **navigational hubs**, not content pages. Link to the new wiki pages; don't duplicate their content here.

3. **Create or update entity pages** in `wiki/entities/` — strict Read-before-Write pattern:
   - For each entity, **first** `Read` the target file path (or check with Glob/ls)
   - **If it exists** → use `Edit` to append new facts, add a row to the Interactions section, and append the new source to the Sources section. Never overwrite.
   - **If it does NOT exist** → use `Write` to create it
   - Entity pages should have: a one-line description, their role/relevance, key topics, interactions, and sources list
   - Use cross-links to concepts and other entities

4. **Create or update concept pages** in `wiki/concepts/` — same strict Read-before-Write pattern:
   - `Read` first. If exists → `Edit` (append). If not → `Write` (create).
   - Concept pages should have: a definition, relevance to your scope, current status, and sources list
   - Cross-link to related concepts, patterns, and entities
   - ⚠️ **Concepts are definitional and stable** — they describe *what something is*. If you find yourself writing an interpretive claim ("users tend to…", "clients reject…"), that belongs in `wiki/patterns/`, not here.

5. **Create or update pattern pages** in `wiki/patterns/` — same strict Read-before-Write pattern:
   - `Read` first. If exists → `Edit` (add new evidence row + bump source_count and confidence). If not → `Write` (create from `wiki/patterns/_template.md`).
   - A pattern page requires **≥2 sources** to be created. If this source is the first occurrence of a signal, note it as a "proto-pattern" in the synthesis page instead. When a second source confirms it, promote it to a full pattern page.
   - Pattern pages must have: observation, evidence table with dated sources, confidence level (weak/moderate/strong), scope (product line, geo, segment), implications, and a contradictions section.
   - When adding evidence to an existing pattern: append a row to the evidence table, bump `source_count` in front-matter, and reassess confidence level if warranted.
   - Cross-link to related concepts, entities, and other patterns.

6. **Update `wiki/index.md` INCREMENTALLY** — this is critical:
   - **Always** `Read` the current `index.md` in full before touching it
   - Use `Edit` to insert new rows into the appropriate existing tables (Entities, Concepts, Patterns, Syntheses, MOCs). **Never** use `Write` on `index.md`.
   - For pattern entries use: `| [Page name](relative/path.md) | confidence | scope | One-line summary |`
   - For other entries: `| [Page name](relative/path.md) | One-line summary |`
   - If you discovered orphan files on disk during Phase 1 step 2, add them to the index in the same pass
   - Preserve the existing category structure and all existing rows verbatim

7. **Append to `wiki/log.md`**:
   - `Read` the file, then `Edit` to append at the end. Never `Write`.
   - Format: `## [YYYY-MM-DD] ingest | <source description>`
   - List: source path, pages created, pages updated (distinguish created vs. updated clearly)
   - This is append-only — never modify existing log entries

## Guidelines

- **Language**: all wiki content (`wiki/`, `index.md`, `log.md`, entity pages, concept pages, pattern pages, syntheses) must be written in **English**, regardless of the source language. Raw sources in `raw/` stay in their original language. This matches the top-level `CLAUDE.md` rule.
- **Cross-links**: use relative markdown links between wiki pages. This is what makes the wiki compound — a well-linked wiki is exponentially more useful than isolated pages.
- **Don't duplicate**: before creating a new entity or concept page, check both the index AND the actual directory. If a page exists, update it instead.
- **Be opinionated about structure**: if the source reveals that an existing wiki page has stale information, update it. If two concepts should be merged, flag it to the user.
- **Preserve existing content**: when updating a page, add to it. Don't delete information from previous ingests unless it's been explicitly contradicted by a newer source.
- **Source attribution**: every wiki page should have a "Sources" section at the bottom listing the raw sources it draws from, with relative links.
- **Fail loudly, not silently**: if a Write call would overwrite an existing file, stop and tell the user rather than proceeding.
