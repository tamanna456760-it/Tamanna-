#!/usr/bin/env python3
"""Evaluate local Tamanna knowledge retrieval on a multilingual fixture.

Run from the repository root:
    python scripts/benchmark_vector_retrieval.py --top-k 3

This 15-case fixture measures retrieval ranking only, not answer correctness or GPT/Gemini
equivalence. The default embedder is API-free; set
TAMANNA_EMBEDDING_PROVIDER=ollama to evaluate a local Ollama embedding model.
"""
from __future__ import annotations

import argparse
import json
import tempfile
import time
from pathlib import Path

from tamanna_ai.knowledge.vector_store import VectorKnowledgeStore


DOCUMENTS = [
    (
        "bengali-knowledge.md",
        "বাংলা জ্ঞানভান্ডার",
        "বাংলা ভাষার জ্ঞানভান্ডারে নথি, প্রশ্ন, উত্তর এবং তথ্য অনুসন্ধান "
        "করা যায়। বাংলা লেখা ও যুক্তাক্ষর সংরক্ষণ গুরুত্বপূর্ণ।",
    ),
    (
        "database-backup.md",
        "Database backup and restore",
        "SQLite database backup restore integrity validation and safe recovery. "
        "A backup must be checked before restoring user data.",
    ),
    (
        "privacy-memory.md",
        "ব্যক্তিগত স্মৃতি ও privacy",
        "ব্যবহারকারীর ব্যক্তিগত স্মৃতি নিরাপদে সংরক্ষণ করতে হবে। "
        "প্রতিটি user-এর knowledge আলাদা রাখতে হবে। Private user data "
        "must remain isolated and protected.",
    ),
    (
        "local-model.md",
        "Local Ollama model",
        "Run a local language model with Ollama without hosted GPT or Gemini APIs. "
        "Local model inference requires available RAM and compute resources.",
    ),
    (
        "android-build.md",
        "Android APK build",
        "Build and test the Android application APK. Debug and release artifacts "
        "are produced by the Android CI workflow.",
    ),
    (
        "api-security.md",
        "API security controls",
        "Protect API endpoints with authentication, authorization, input validation, "
        "secure headers, and audit logging. Never commit passwords or API secrets.",
    ),
    (
        "rate-limits.md",
        "Rate limiting",
        "Rate limiting controls request volume per client and endpoint. Return HTTP 429 "
        "when a client exceeds the configured request quota.",
    ),
    (
        "dns-deployment.md",
        "DNS and website deployment",
        "Website deployment requires correct DNS records, domain ownership, TLS "
        "certificates, and a successful hosting build.",
    ),
    (
        "voice-interface.md",
        "Voice interface",
        "A voice interface converts speech to text and can synthesize spoken responses. "
        "Microphone permission is required before recording.",
    ),
    (
        "rag-pipeline.md",
        "Retrieval augmented generation",
        "A RAG pipeline retrieves relevant knowledge chunks, adds grounded context, "
        "and then generates an answer with source references.",
    ),
    (
        "backup-schedule.md",
        "Scheduled backup",
        "Automated database backups should run on a schedule, retain multiple recovery "
        "points, and verify integrity before restore.",
    ),
    (
        "bengali-unicode.md",
        "বাংলা ইউনিকোড ও যুক্তাক্ষর",
        "বাংলা ইউনিকোড টেক্সট স্বাভাবিকীকরণ, কারচিহ্ন এবং যুক্তাক্ষর ঠিকভাবে "
        "সংরক্ষণ করতে হবে। অনুসন্ধানে combining mark বাদ দেওয়া যাবে না।",
    ),
    (
        "user-isolation.md",
        "ব্যবহারকারীভিত্তিক তথ্য বিচ্ছিন্নতা",
        "প্রতিটি ব্যবহারকারীর ব্যক্তিগত নথি, কথোপকথন এবং স্মৃতি আলাদা রাখতে হবে। "
        "একজন ব্যবহারকারী অন্যের গোপন তথ্য দেখতে পারবে না।",
    ),
    (
        "ollama-memory.md",
        "Ollama RAM requirements",
        "Local Ollama model loading depends on model size, available system RAM, "
        "GPU memory, context length, and concurrent requests.",
    ),
    (
        "ci-workflow.md",
        "Continuous integration",
        "Continuous integration runs automated tests, static checks, security scans, "
        "and build validation for every relevant commit.",
    ),
    (
        "hindi-knowledge.md",
        "हिंदी ज्ञान खोज",
        "हिंदी भाषा में ज्ञान दस्तावेज़, प्रश्न और उत्तर खोजे जा सकते हैं। "
        "देवनागरी यूनिकोड और मात्रा को सुरक्षित रखना महत्वपूर्ण है।",
    ),
    (
        "arabic-knowledge.md",
        "البحث في المعرفة العربية",
        "يمكن البحث في مستندات المعرفة باللغة العربية. "
        "يجب الحفاظ على حروف العربية والتشكيل واتجاه الكتابة من اليمين إلى اليسار.",
    ),
]

CASES = [
    {"query": "বাংলা ভাষার জ্ঞানভান্ডার অনুসন্ধান", "relevant": "bengali-knowledge.md", "language": "bn"},
    {"query": "SQLite backup restore integrity", "relevant": "database-backup.md", "language": "en"},
    {"query": "ব্যক্তিগত স্মৃতি এবং user data নিরাপত্তা", "relevant": "privacy-memory.md", "language": "mixed"},
    {"query": "local Ollama model without GPT Gemini API", "relevant": "local-model.md", "language": "en"},
    {"query": "Android APK release build test", "relevant": "android-build.md", "language": "en"},
    {"query": "API authentication secret নিরাপত্তা audit log", "relevant": "api-security.md", "language": "mixed"},
    {"query": "HTTP 429 request quota rate limit", "relevant": "rate-limits.md", "language": "en"},
    {"query": "ডোমেইন DNS record TLS website deployment", "relevant": "dns-deployment.md", "language": "bn"},
    {"query": "microphone speech to text voice response", "relevant": "voice-interface.md", "language": "en"},
    {"query": "RAG retrieve knowledge chunks grounded context", "relevant": "rag-pipeline.md", "language": "en"},
    {"query": "database scheduled backup recovery integrity", "relevant": "backup-schedule.md", "language": "en"},
    {"query": "বাংলা ইউনিকোড কারচিহ্ন যুক্তাক্ষর অনুসন্ধান", "relevant": "bengali-unicode.md", "language": "bn"},
    {"query": "ব্যবহারকারীর ব্যক্তিগত নথি এবং memory isolation", "relevant": "user-isolation.md", "language": "mixed"},
    {"query": "Ollama model RAM GPU context length", "relevant": "ollama-memory.md", "language": "en"},
    {"query": "CI automated tests security scan build validation", "relevant": "ci-workflow.md", "language": "en"},
    {"query": "हिंदी भाषा ज्ञान दस्तावेज़ खोज", "relevant": "hindi-knowledge.md", "language": "hi"},
    {"query": "البحث عن مستندات المعرفة العربية", "relevant": "arabic-knowledge.md", "language": "ar"},
]


def evaluate(store: VectorKnowledgeStore, *, top_k: int = 3) -> dict:
    """Return hit-rate and mean reciprocal rank for the fixed multilingual cases."""
    if not 1 <= top_k <= 20:
        raise ValueError("top_k must be between 1 and 20")

    reciprocal_ranks = []
    hits = 0
    details = []
    language_stats: dict[str, dict[str, float | int]] = {}
    for case in CASES:
        started = time.perf_counter()
        results = store.search(case["query"], owner_id="benchmark", limit=top_k)
        elapsed_ms = (time.perf_counter() - started) * 1000
        rank = next(
            (index for index, item in enumerate(results, start=1)
             if item["source"] == case["relevant"]),
            None,
        )
        if rank is not None:
            hits += 1
        reciprocal_rank = 1.0 / rank if rank else 0.0
        reciprocal_ranks.append(reciprocal_rank)
        language = case["language"]
        bucket = language_stats.setdefault(language, {"cases": 0, "hits": 0, "reciprocal_rank_sum": 0.0})
        bucket["cases"] += 1
        bucket["hits"] += int(rank is not None)
        bucket["reciprocal_rank_sum"] += reciprocal_rank
        details.append({
            "language": language,
            "query": case["query"],
            "expected_source": case["relevant"],
            "retrieved_sources": [item["source"] for item in results],
            "relevant_rank": rank,
            "latency_ms": round(elapsed_ms, 3),
        })

    total = len(CASES)
    by_language = {
        language: {
            "cases": stats["cases"],
            "hit_rate": round(stats["hits"] / stats["cases"], 4),
            "mean_reciprocal_rank": round(stats["reciprocal_rank_sum"] / stats["cases"], 4),
        }
        for language, stats in sorted(language_stats.items())
    }
    return {
        "cases": total,
        "top_k": top_k,
        "hit_rate": round(hits / total, 4),
        "mean_reciprocal_rank": round(sum(reciprocal_ranks) / total, 4),
        "by_language": by_language,
        "results": details,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--top-k", type=int, default=3)
    args = parser.parse_args()
    if not 1 <= args.top_k <= 20:
        parser.error("--top-k must be between 1 and 20")

    with tempfile.TemporaryDirectory(prefix="tamanna-vector-eval-") as directory:
        store = VectorKnowledgeStore(db_path=Path(directory) / "evaluation.sqlite3")
        for source, title, content in DOCUMENTS:
            store.index_text(
                content, owner_id="benchmark", source=source, title=title
            )
        report = evaluate(store, top_k=args.top_k)
        report["embedding_provider"] = type(store.embedder).__name__
        print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
