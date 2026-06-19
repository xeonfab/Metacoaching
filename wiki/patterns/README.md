# 🔍 Patterns

> Observed, interpreted signals from the field. **One MD file per pattern.**

This folder captures the *so what* — recurring behaviors, objections, preferences, or failure modes you've **observed across multiple sources**. Unlike concepts (which are definitional and stable), patterns are interpretive, rankable, and perishable.

---

## What goes here

✅ **Yes**
- User behaviors: "DAFs systematically reject invoices without PO"
- Adoption signals: "Italian clients always ask about SDI before signing"
- Objections & friction: "Sales blockers around multi-entity treasury"
- Failure modes: "CSV imports break on encoding 80% of the time"
- Workarounds: "Clients create dummy suppliers to bypass approval flow"

❌ **No**
- Definitions or standards → `wiki/concepts/`
- People or companies → `wiki/entities/`
- One-off anecdotes with no recurring evidence → stays in `wiki/syntheses/`

> **Rule of thumb**: if it's a *claim about reality* that you could rank, refute, or watch evolve — it's a pattern, not a concept.

---

## Filename convention

`Pattern_Short_Name.md` — underscore separator, descriptive.

Examples: `DAF_Reject_No_PO.md`, `Italian_SDI_Blocker.md`, `CSV_Encoding_Failures.md`.

---

## Schema

Copy [`_template.md`](_template.md) to start. Every pattern page should have:

- **Front-matter** with `last_reviewed`, `confidence`, `source_count`
- **Observation** — what you see happening, in 1-3 lines
- **Evidence** — list of sources with dates (minimum 2 to qualify as a pattern)
- **Confidence** — how strong is this signal (🔴 weak / 🟡 moderate / 🟢 strong)
- **Scope** — where does this apply (product line, geography, segment)
- **Implications** — so what? What should we do about it?
- **Contradictions** — any counter-evidence or exceptions
- **Related** — cross-links to concepts, entities, other patterns

---

## Philosophy

Patterns are where the wiki becomes **opinionated**. Concepts tell you what things are; patterns tell you what's actually happening. They're the bridge between raw meeting notes and strategic insight.

Patterns earn their keep by being **falsifiable**: a pattern with counter-evidence listed is more valuable than one without, because you can track whether it's strengthening or weakening over time.

A pattern with only 1 source is just an anecdote — keep it in syntheses until you see it again.
