# 📝 Syntheses

> Cross-source analyses, meeting summaries, project pages, strategy notes. **One MD file per synthesis.**

This folder captures the *so what* — the compiled, interpreted output that draws on multiple sources.

---

## What goes here

✅ **Yes**
- Meeting summaries (1:1s, weeklies, kickoffs, demos, client calls)
- Project pages (long-lived initiatives)
- Strategy notes (vision docs, market analyses, OKR breakdowns)
- Competitor deep dives
- Saved queries (cross-cutting questions you'll re-ask — e.g., "what's happening on Italy?")

❌ **No**
- Raw transcripts → `raw/transcripts/`
- People dossiers → `wiki/entities/`

> **Rule of thumb**: if it synthesizes 2+ sources into a reusable takeaway, it's a synthesis.

---

## Subfolders

- `syntheses/meetings/` — meeting summaries (1:1s, weeklies, kickoffs, demos, client calls). Add `meetings/YYYY/` sub-level when volume grows.
- `syntheses/projects/` — long-lived initiatives (e.g., `payment-campaigns.md`, `vendor-management.md`)
- `syntheses/competitors/` — competitor analyses
- `syntheses/strategy/` — vision, OKRs, market docs
- `syntheses/research/` — saved queries, cross-cutting analyses, ad-hoc deep dives that don't fit elsewhere

---

## Filename convention

- **Meetings & calls**: `meetings/YYYY-MM-DD_<descriptive-slug>.md` — e.g. `meetings/2026-04-20_thermocompact-p2p-followup.md`
- **Projects**: `projects/<project-slug>.md` — e.g. `payment-campaigns.md`
- **Competitors**: `competitors/<Competitor>_<topic>.md` — e.g. `Ramp_Competitive_Analysis.md`
- **Strategy**: `strategy/<slug>.md` — e.g. `okr-2026.md`
- **Research**: `research/<slug>.md` — e.g. `italy-market-overview.md`

---

## Schema

Every synthesis page should have:

- **Front-matter** with `last_reviewed: YYYY-MM-DD`
- **Context** — date, participants (for meetings), source(s)
- **Key points** organised by theme
- **Decisions & next steps** (for meetings)
- **Links** — entities, concepts touched
- **Sources** — relative paths to raw files

---

## Philosophy

Syntheses are the **compound interest** of the wiki. Raw sources alone are noise; syntheses extract signal. A well-written synthesis is re-readable six months later and can answer "what did we decide about X?" in 30 seconds.

Cross-link heavily — each synthesis should touch 3-5 entity/concept pages minimum.
