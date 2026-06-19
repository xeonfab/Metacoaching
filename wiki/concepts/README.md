# 📚 Concepts

> Technical or business concepts in your scope. **One MD file per concept.**

This folder captures the *what* — the standards, protocols, business objects, workflows, or vocabulary items that recur in your work.

---

## What goes here

✅ **Yes**
- Technical standards & formats (pain.001, ISO 20022, EBICS, SEPA, CAMT.053…)
- Business concepts (3-way matching, Cash Application, Schedule Payment…)
- Internal vocabulary (SIM, P2P, PA, PSR…)
- Workflows / processes
- Product features at the platform level

❌ **No**
- People → `wiki/entities/`
- Interpreted signals, recurring behaviors, user objections → `wiki/patterns/` (e.g., "DAFs reject invoices without PO" is a **pattern**, not a concept)

> **Rule of thumb**: if you've had to explain it 2+ times, it deserves a page.

---

## Filename convention

`Concept_Name.md` — underscore separator, keep it short and recognisable.

Examples: `pain_001.md`, `EBICS.md`, `3_way_matching.md`, `Cash_Application.md`.

---

## Schema

Copy [`_template.md`](_template.md) to start. Every concept page should have:

- **Front-matter** with `last_reviewed: YYYY-MM-DD`
- **Definition** — what is this, in 1-3 lines
- **Why it matters at Agicap** — connect to your product lines
- **Current status** — is this in production / planned / deprecated
- **Related** — cross-links to adjacent concepts and entities
- **Sources** — raw files that fed this page

---

## Philosophy

Concept pages are your **vocabulary**. Cross-linked concepts form a knowledge graph that compounds: the more concepts you capture, the more Claude can connect them when synthesizing a meeting, a strategy note, or a competitor brief.

Don't over-engineer. A stub concept page (3 lines + 1 source) is infinitely better than no page.
