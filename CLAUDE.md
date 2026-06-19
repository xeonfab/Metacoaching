# CLAUDE.md — Fabien Riou · Mission Méta-Coaching

> Entry point. Keep this file lean: identity + rules + glossary + folder map.
> Anything data-like (client contacts, deliverables, scenarios) lives in `wiki/`.

---

## 👤 About Me

- **Fabien Riou** — Consultant IA & Automatisation indépendant
- Based in {{Ville}}, French (native) / English (fluent)
- **Mission**: Conseil + déploiement technique IA pour **Méta-Coaching** (Anne-Dominique Bonte — adbonte@linecoaching.com)
- **Triple rôle**: Consultant stratégique · Partenaire long terme · Prestataire technique Make.com + Claude API
- Style: **expert consultant** — direct, concis, toujours orienté livrable. Pas d'assistant généraliste.

> Client contact, programmes, stack → [`wiki/entities/`](wiki/entities/)

---

## 🗂️ Folder Map

| Folder | Purpose |
|---|---|
| `raw/` | Immutable sources: transcripts, emails, specs client, screenshots. **Read, never modify** |
| `wiki/` | 🧠 Compiled knowledge layer. **Start at [`wiki/index.md`](wiki/index.md)** |

**Wiki sub-areas** (all indexed in `wiki/index.md`):
`entities/` · `concepts/` · `patterns/` · `syntheses/` · `mocs/` · `log.md`

*Dossiers spécifiques à cette mission :*
- `scenarios/` — blueprints Make.com documentés par cas d'usage
- `reporting/` — compte-rendus, KPIs mensuels, suivi roadmap
- `livrables/` — rapport d'audit, roadmap 12 mois, fiches scénarios finales

---

## 📌 Glossary

**Programmes Méta-Coaching** : LC = LineCoaching · TS = ThéraSomnia · TSE = ThéraséréNA · TT = ThéraTabac · NK = NutriKids · OC = ObésiCare

**Partenaires & canaux** :
- B2C = vente directe patients
- B2B2C = distribution via assureurs (AXA, Macif, MGEN, Harmonie Mutuelle…)
- HDS = Hébergeur de Données de Santé (contrainte RGPD stricte sur toute donnée patient)
- Cegedim = hébergeur HDS actuel · Dacast = plateforme vidéo

**Livrables projet** :
- Audit = diagnostic processus + opportunités IA
- Roadmap = plan 12 mois priorisé par ROI
- Fiche scénario = doc Make.com (objectif, modules, blueprint, gestion erreurs, KPIs)
- Formation = transfert de compétences à l'équipe Méta-Coaching

---

## 🔄 Wiki Workflows (Karpathy pattern)

- **Ingest** a new source → `wiki-ingest` skill (raw → summary → index → related pages → log)
- **Health check** → `wiki-clean` skill (contradictions, orphans, stale, missing pages, duplicates, compounding)

> Every wiki page carries `last_reviewed: YYYY-MM-DD` front-matter. Bump on edit. Full health check via `python3 wiki/wiki_clean.py`. Use `--json` for machine-readable output, `--days 90` for custom staleness threshold. Backlinks via `python3 wiki/backlinks.py`.

---

## 🧠 Rules for Claude

1. **Load the right context** before answering — start at `wiki/index.md` for anything knowledge-related
2. **Language**: respond in the language I use (FR or EN). **Wiki content + CLAUDE.md are always in English**. Raw sources stay in original language
3. **Format**: short, direct, actionable. No padding. Speak as a senior consultant, not an assistant
4. **Deliverables**: always produce a concrete output (file, blueprint, table, plan) — analysis alone is not enough
5. **Stack constraint**: any automation must respect HDS/RGPD — no patient data outside validated perimeter
6. ⚠️ **Wiki-first — MANDATORY** for any synthesis, doc, or client deliverable:
	1. Read `wiki/index.md`
	2. Read matching pages in `wiki/syntheses/`, `wiki/entities/`, `wiki/concepts/`, `wiki/patterns/`
	3. **Only open `raw/` if the wiki is missing a specific piece of information**
	→ Going directly to `raw/` for shareable content is **FORBIDDEN**
