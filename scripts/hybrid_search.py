#!/usr/bin/env python3
"""
Hybrid search engine for Méta-Coaching wiki.
Combines BM25 (keyword) + semantic embeddings (Ollama) for retrieval.

Usage:
    # First-time indexing
    python3 scripts/hybrid_search.py --index

    # Search
    python3 scripts/hybrid_search.py "preuves cliniques ThéraSomnia"
    python3 scripts/hybrid_search.py "reporting AXA mensuel" --top 5
    python3 scripts/hybrid_search.py "restriction cognitive" --domain clinique

    # Re-index after wiki changes
    python3 scripts/hybrid_search.py --reindex

    # JSON output (for Make.com / n8n integration)
    python3 scripts/hybrid_search.py "dropout prediction" --json

Requirements:
    pip install rank-bm25 numpy requests
    Ollama running locally with an embedding model:
        ollama pull nomic-embed-text
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import sys
import time
from pathlib import Path
from typing import Optional

import numpy as np
import requests
from rank_bm25 import BM25Okapi

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

WIKI_DIR = Path(__file__).resolve().parent.parent / "wiki"
RAW_DIR = Path(__file__).resolve().parent.parent / "raw"
INDEX_DIR = Path(__file__).resolve().parent.parent / ".search_index"

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
EMBED_MODEL = os.environ.get("EMBED_MODEL", "nomic-embed-text")

CHUNK_SIZE = 800
CHUNK_OVERLAP = 100

# Domain routing: maps domain keywords to wiki subfolders
DOMAIN_FOLDERS = {
    "clinique": ["concepts", "entities"],
    "ops": ["syntheses"],
    "assureurs": ["entities", "syntheses"],
    "all": ["concepts", "entities", "patterns", "syntheses", "mocs"],
}

SKIP_FILES = {"_template.md", "README.md", "Example_Person.md",
              "Example_Concept.md", "Example_Pattern.md"}

# ---------------------------------------------------------------------------
# Text processing
# ---------------------------------------------------------------------------

FRONTMATTER_RE = re.compile(r"^---\n.*?\n---\n?", re.DOTALL)
BACKLINKS_RE = re.compile(
    r"<!-- BACKLINKS:START -->.*?<!-- BACKLINKS:END -->\n?", re.DOTALL
)


def clean_md(text: str) -> str:
    text = FRONTMATTER_RE.sub("", text)
    text = BACKLINKS_RE.sub("", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)  # strip md links
    text = re.sub(r"[#*_`>|]", " ", text)  # strip md formatting
    text = re.sub(r"-{3,}", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def chunk_text(text: str, source_path: str) -> list[dict]:
    words = text.split()
    if not words:
        return []
    chunks = []
    start = 0
    while start < len(words):
        end = start + CHUNK_SIZE
        chunk_words = words[start:end]
        chunk_text_str = " ".join(chunk_words)
        chunks.append({
            "text": chunk_text_str,
            "source": source_path,
            "chunk_id": f"{source_path}::{start}",
        })
        start += CHUNK_SIZE - CHUNK_OVERLAP
    return chunks


def tokenize(text: str) -> list[str]:
    text = text.lower()
    text = re.sub(r"[^a-zàâäéèêëïîôùûüÿçœæ0-9\s]", " ", text)
    return [w for w in text.split() if len(w) > 1]


# ---------------------------------------------------------------------------
# Ollama embeddings
# ---------------------------------------------------------------------------

def get_embedding(text: str) -> Optional[list[float]]:
    try:
        resp = requests.post(
            f"{OLLAMA_URL}/api/embed",
            json={"model": EMBED_MODEL, "input": text},
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
        if "embeddings" in data and data["embeddings"]:
            return data["embeddings"][0]
        return None
    except Exception as e:
        print(f"  [warn] Embedding failed: {e}", file=sys.stderr)
        return None


def cosine_similarity(a: list[float], b: list[float]) -> float:
    a_np, b_np = np.array(a), np.array(b)
    dot = np.dot(a_np, b_np)
    norm = np.linalg.norm(a_np) * np.linalg.norm(b_np)
    if norm == 0:
        return 0.0
    return float(dot / norm)


# ---------------------------------------------------------------------------
# Indexing
# ---------------------------------------------------------------------------

def collect_documents(domain: str = "all") -> list[dict]:
    folders = DOMAIN_FOLDERS.get(domain, DOMAIN_FOLDERS["all"])
    docs = []

    # Wiki pages
    for folder in folders:
        folder_path = WIKI_DIR / folder
        if not folder_path.exists():
            continue
        for md_file in sorted(folder_path.rglob("*.md")):
            if md_file.name in SKIP_FILES:
                continue
            text = md_file.read_text(encoding="utf-8", errors="replace")
            clean = clean_md(text)
            if len(clean) < 50:
                continue
            rel_path = str(md_file.relative_to(WIKI_DIR.parent))
            docs.append({"path": rel_path, "text": clean, "type": "wiki"})

    # Raw sources (articles, transcripts)
    for subfolder in ["articles", "transcripts", "specs"]:
        raw_path = RAW_DIR / subfolder
        if not raw_path.exists():
            continue
        for f in sorted(raw_path.rglob("*.md")):
            text = f.read_text(encoding="utf-8", errors="replace")
            clean = clean_md(text)
            if len(clean) < 50:
                continue
            rel_path = str(f.relative_to(WIKI_DIR.parent))
            docs.append({"path": rel_path, "text": clean, "type": "raw"})

    return docs


def build_index(domain: str = "all") -> dict:
    print(f"Collecting documents (domain={domain})...")
    docs = collect_documents(domain)
    print(f"Found {len(docs)} documents")

    all_chunks = []
    for doc in docs:
        chunks = chunk_text(doc["text"], doc["path"])
        for c in chunks:
            c["doc_type"] = doc["type"]
        all_chunks.extend(chunks)
    print(f"Created {len(all_chunks)} chunks")

    # BM25 index
    print("Building BM25 index...")
    tokenized_corpus = [tokenize(c["text"]) for c in all_chunks]
    bm25 = BM25Okapi(tokenized_corpus)

    # Embeddings
    print(f"Generating embeddings via {EMBED_MODEL}...")
    embeddings = []
    for i, chunk in enumerate(all_chunks):
        if (i + 1) % 10 == 0 or i == 0:
            print(f"  [{i+1}/{len(all_chunks)}] {chunk['source'][:60]}...")
        emb = get_embedding(chunk["text"])
        embeddings.append(emb)

    valid_count = sum(1 for e in embeddings if e is not None)
    print(f"Generated {valid_count}/{len(all_chunks)} embeddings")

    index = {
        "chunks": all_chunks,
        "tokenized": tokenized_corpus,
        "embeddings": embeddings,
        "domain": domain,
        "created": time.strftime("%Y-%m-%d %H:%M:%S"),
        "doc_count": len(docs),
        "chunk_count": len(all_chunks),
    }

    # Save
    INDEX_DIR.mkdir(exist_ok=True)
    index_path = INDEX_DIR / f"index_{domain}.json"

    serializable = {
        "chunks": all_chunks,
        "tokenized": tokenized_corpus,
        "embeddings": [e if e is not None else [] for e in embeddings],
        "domain": domain,
        "created": index["created"],
        "doc_count": index["doc_count"],
        "chunk_count": index["chunk_count"],
    }
    with open(index_path, "w", encoding="utf-8") as f:
        json.dump(serializable, f, ensure_ascii=False)
    size_mb = index_path.stat().st_size / (1024 * 1024)
    print(f"Index saved: {index_path} ({size_mb:.1f} MB)")

    return index


def load_index(domain: str = "all") -> Optional[dict]:
    index_path = INDEX_DIR / f"index_{domain}.json"
    if not index_path.exists():
        return None
    with open(index_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    data["embeddings"] = [e if e else None for e in data["embeddings"]]
    return data


# ---------------------------------------------------------------------------
# Search
# ---------------------------------------------------------------------------

def hybrid_search(
    query: str,
    index: dict,
    top_k: int = 3,
    bm25_weight: float = 0.4,
    semantic_weight: float = 0.6,
) -> list[dict]:
    chunks = index["chunks"]
    tokenized = index["tokenized"]
    embeddings = index["embeddings"]

    if not chunks:
        return []

    # BM25 scores
    bm25 = BM25Okapi(tokenized)
    query_tokens = tokenize(query)
    bm25_scores = bm25.get_scores(query_tokens)

    # Normalize BM25
    bm25_max = max(bm25_scores) if max(bm25_scores) > 0 else 1.0
    bm25_norm = [s / bm25_max for s in bm25_scores]

    # Semantic scores
    query_emb = get_embedding(query)
    if query_emb is not None:
        sem_scores = []
        for emb in embeddings:
            if emb is not None:
                sem_scores.append(cosine_similarity(query_emb, emb))
            else:
                sem_scores.append(0.0)
        sem_max = max(sem_scores) if max(sem_scores) > 0 else 1.0
        sem_norm = [s / sem_max for s in sem_scores]
    else:
        sem_norm = [0.0] * len(chunks)
        bm25_weight = 1.0
        semantic_weight = 0.0

    # Hybrid score
    hybrid_scores = []
    for i in range(len(chunks)):
        score = bm25_weight * bm25_norm[i] + semantic_weight * sem_norm[i]
        hybrid_scores.append(score)

    # Deduplicate by source (keep best chunk per document)
    source_best: dict[str, tuple[float, int]] = {}
    for i, score in enumerate(hybrid_scores):
        src = chunks[i]["source"]
        if src not in source_best or score > source_best[src][0]:
            source_best[src] = (score, i)

    ranked = sorted(source_best.items(), key=lambda x: -x[1][0])[:top_k]

    results = []
    for source, (score, idx) in ranked:
        chunk = chunks[idx]
        results.append({
            "source": source,
            "score": round(score, 4),
            "bm25_score": round(bm25_norm[idx], 4),
            "semantic_score": round(sem_norm[idx], 4),
            "doc_type": chunk.get("doc_type", "unknown"),
            "excerpt": chunk["text"][:300] + "..." if len(chunk["text"]) > 300 else chunk["text"],
        })
    return results


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(
        description="Hybrid search (BM25 + embeddings) for Méta-Coaching wiki"
    )
    ap.add_argument("query", nargs="?", help="Search query")
    ap.add_argument("--index", action="store_true", help="Build index")
    ap.add_argument("--reindex", action="store_true", help="Rebuild index")
    ap.add_argument("--domain", default="all",
                    choices=["all", "clinique", "ops", "assureurs"],
                    help="Restrict search to a domain")
    ap.add_argument("--top", type=int, default=3, help="Number of results")
    ap.add_argument("--json", action="store_true", help="JSON output")
    ap.add_argument("--bm25-weight", type=float, default=0.4)
    ap.add_argument("--semantic-weight", type=float, default=0.6)
    args = ap.parse_args()

    if args.index or args.reindex:
        build_index(args.domain)
        return

    if not args.query:
        ap.print_help()
        return

    index = load_index(args.domain)
    if index is None:
        print(f"No index found for domain '{args.domain}'. Run with --index first.")
        sys.exit(1)

    results = hybrid_search(
        args.query,
        index,
        top_k=args.top,
        bm25_weight=args.bm25_weight,
        semantic_weight=args.semantic_weight,
    )

    if args.json:
        print(json.dumps({"query": args.query, "results": results}, indent=2, ensure_ascii=False))
    else:
        print(f"\n{'='*60}")
        print(f"Query: {args.query}")
        print(f"Domain: {args.domain} | Results: {len(results)}")
        print(f"{'='*60}\n")
        for i, r in enumerate(results, 1):
            print(f"  [{i}] {r['source']}")
            print(f"      Score: {r['score']} (BM25: {r['bm25_score']} | Semantic: {r['semantic_score']})")
            print(f"      Type: {r['doc_type']}")
            print(f"      Excerpt: {r['excerpt'][:150]}...")
            print()


if __name__ == "__main__":
    main()
