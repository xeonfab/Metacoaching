# 🧠 PM LLM Wiki — Starter Pack

> A second-brain setup for Agicap PMs, following Andrej Karpathy's [LLM Wiki pattern](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f).
> **Goal**: compound your knowledge so Claude becomes an actual workplace collaborator, not just a one-shot assistant.

---

## 🗺️ A generic starting point — make it yours

This folder structure is intentionally generic so it works for any role at the company. The real value comes from adapting it to your context: a PM might synthesize raw call transcripts into product insights, then aggregate them into feature pages. An ops person might track vendor relationships and process docs instead. Start here, then shape it around how *you* actually think.

Videos to get started :
- Video 1 : https://www.loom.com/share/deafe6e53038465ca7fcfe6a070b0345
- Video 2 : https://www.loom.com/share/efaa2171adfb452fa7318c9dc025b57f

---

## 🎯 What is this?

A file-based knowledge system your LLM maintains with you. Three layers:

1. **`raw/`** — immutable sources: transcripts, articles, specs, screenshots. Read, never modify.
2. **`wiki/`** — your compiled, cross-linked knowledge graph (entities, concepts, syntheses, MOCs).
3. **`CLAUDE.md`** — identity + rules at the root. Claude reads this first.

Two skills drive the workflow:
- **`wiki-ingest`** — pastes a transcript / article / thread into the wiki, creating / updating entity + concept + synthesis pages in one pass.
- **`wiki-clean`** — weekly health check: orphans, stale pages, contradictions, missing concepts, broken links.

Two scripts keep the graph tight:
- **`backlinks.py`** — regenerates the `## Referenced by` block on every page (reverse index).
- **`wiki_clean.py`** — full health check: stale pages, duplicates, contradictions, compounding-without-evidence.

---

## 🛠️ Prerequisites

- **Claude Code** or **Cowork mode** (both work — scripts are IDE-agnostic)
- **Python 3.8+** on your machine (for the two scripts)
- A folder on your computer where this will live (e.g., `~/Claude/` or wherever you want)
- Optional but nice: **VS Code**, **Cursor**, or **Obsidian** for a graph view (not required — any editor works)

---

## 🚀 Install in 5 steps

### 1. Copy the starter pack into your workspace

Copy this entire `starter-pack/` folder into your chosen workspace location (e.g., rename it to `Claude/`). The structure should look like:

```
Claude/
├── CLAUDE.md
├── README.md                  ← this file (delete or keep as reference)
├── .gitignore
├── raw/
│   ├── articles/  transcripts/  specs/  screenshots/
├── wiki/
│   ├── index.md  log.md
│   ├── backlinks.py  wiki_clean.py
│   ├── entities/  concepts/  patterns/  syntheses/  mocs/
│   │   └── (each with README.md + _template.md)
└── skills/
    ├── wiki-ingest/SKILL.md
    └── wiki-clean/SKILL.md
```

### 2. Install the skills

Just ask Claude to create the skills for you based on the files in the `skills/` folder:

> "Create the wiki-ingest and wiki-clean skills from the SKILL.md files in my skills/ folder"

Claude will set them up in the right place. Once done, they auto-trigger on phrases like "ingest this", "clean the wiki", "what's in this transcript".

### 3. Fill in `CLAUDE.md`

Just ask Claude to do it:

> "Help me fill in my CLAUDE.md — ask me the questions you need"

Claude will walk you through it. Keep it lean — team roster and detailed context belong in `wiki/entities/`, not here.

### 4. Seed with one source

Grab the transcript of your most recent meeting (or an article you want to retain) and tell Claude:

> "Ingest this transcript"
> *(paste content)*

The `wiki-ingest` skill will:
1. Save the raw source to `raw/transcripts/`
2. Show you a takeaways summary (entities, concepts, patterns) — **you validate**
3. On your OK, create a synthesis page + entity pages + concept pages, update `wiki/index.md` and `wiki/log.md`

### 5. Run your first clean

After 3-5 ingests, ask Claude:

> "Clean the wiki"

You'll get a health report (orphans, missing concepts, stale pages) + proposed fixes you can approve one by one.

---

## 🔁 The weekly rhythm

| When | Action | How |
|---|---|---|
| **After every meaningful meeting / call / article** | Ingest | "Ingest this" |
| **Weekly (Friday / Monday AM)** | Clean | "Clean the wiki" |
| **Monthly** | Health check | `python3 wiki/wiki_clean.py` |
| **Quarterly** | Refactor | Merge duplicates, split bloated pages, build MOCs |

---

## 🧩 Folder cheat-sheet

| Folder | What goes in | Example |
|---|---|---|
| `wiki/entities/` | People, orgs, clients, banks | `Hind_Bidal.md`, `Societe_Generale.md` |
| `wiki/concepts/` | Technical / business concepts | `pain_001.md`, `3_way_matching.md` |
| `wiki/patterns/` | Recurring behaviours, anti-patterns, decision heuristics | `pattern_late_payment_cascade.md`, `pattern_approval_bottleneck.md` |
| `wiki/syntheses/` | Meeting summaries, projects, strategy, competitor analyses | `2026-04-20_thermocompact-p2p.md`, `syntheses/projects/payment-campaigns.md` |
| `wiki/mocs/` | Thematic maps of content | `MOC_E-invoicing.md`, `MOC_Payments.md` |

Each folder has a `README.md` explaining the schema + a `_template.md` to copy when creating a new page.

---

## ❓ FAQ

**Do I need Obsidian?**
No. Obsidian gives you a nice graph view and free backlinks rendering, but everything here works the same in VS Code / Cursor / Vim. The two Python scripts replicate backlink generation without any IDE-specific feature.

**Can I version-control this with git?**
Yes — recommended. The `.gitignore` already excludes binary blobs from `raw/screenshots/` and Python cache files. Usage of Github between Agicap is under discussion.

**What if my wiki gets too big?**
That's the point — it compounds. The `wiki-clean` skill keeps it tidy. If one concept page gets too long, split it. If two concepts keep being mentioned together, consider a MOC.

**Can I share my wiki with my squad?**
Discussions are ongoing, but we want to avoid unnecessary conflicts with Notion. We recommand that you test this setup locally, and tell us what you think should remain in Notion !

**What about sensitive info?**
Treat it like any internal doc. Don't put passwords, client PII beyond what's already in Slack/Notion, or un-anonymised legal content.

---

## 🧪 Seeded example

This starter pack ships with a tiny seeded example to show cross-linking in action:
- `wiki/entities/Example_Person.md`
- `wiki/concepts/Example_Concept.md`
- `wiki/syntheses/2026-04-21_example-kickoff.md`

Open them, trace the links between them, then **delete all three** once you're comfortable.

---

## 🤝 Questions / improvements?

Ping Joseph RD on Slack. This setup will evolve — suggestions welcome.

---

## 📚 Credits

- [Andrej Karpathy — LLM Wiki gist](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)
- [Karpathy tweet](https://x.com/karpathy/status/2039805659525644595)
