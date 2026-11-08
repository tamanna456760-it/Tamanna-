#!/usr/bin/env python3
"""Opt-in SQLite benchmark for Tamanna AI lexical knowledge retrieval.

Run from the repository root:
    python scripts/benchmark_knowledge_search.py --sizes 10000 100000 --repeats 3

This measures local synthetic-data search latency; it is not a quality benchmark
and does not imply neural or semantic retrieval performance.
"""
from __future__ import annotations

import argparse
import json
import statistics
import tempfile
import time
from pathlib import Path

from tamanna_ai.memory.knowledge_import import search_knowledge
from tamanna_ai.persistence.database import Database, Memory


def seed_database(database: Database, row_count: int, batch_size: int = 1000) -> None:
    database.init()
    metadata = json.dumps({"kind": "imported_knowledge", "source": "synthetic-benchmark"})
    with database.Session() as session:
        for start in range(0, row_count, batch_size):
            end = min(start + batch_size, row_count)
            session.add_all(
                Memory(
                    user_id=None,
                    content=(
                        f"Synthetic knowledge record {index}. "
                        "Common retrieval marker tamanna benchmark scalability."
                        if index % 100 == 0
                        else f"Synthetic knowledge record {index}. General reference text."
                    ),
                    metadata_json=metadata,
                )
                for index in range(start, end)
            )
            session.commit()


def benchmark_size(row_count: int, repeats: int) -> dict[str, float | int]:
    with tempfile.TemporaryDirectory(prefix="tamanna-knowledge-bench-") as temp_dir:
        database = Database(f"sqlite:///{Path(temp_dir) / 'benchmark.sqlite3'}")
        seed_started = time.perf_counter()
        seed_database(database, row_count)
        seed_seconds = time.perf_counter() - seed_started

        timings = []
        result_count = 0
        for _ in range(repeats):
            started = time.perf_counter()
            results = search_knowledge("tamanna benchmark scalability", database=database, limit=5)
            timings.append(time.perf_counter() - started)
            result_count = len(results)

        return {
            "records": row_count,
            "seed_seconds": round(seed_seconds, 3),
            "median_search_ms": round(statistics.median(timings) * 1000, 3),
            "p95_search_ms": round(sorted(timings)[max(0, int(0.95 * len(timings) + 0.999999) - 1)] * 1000, 3),
            "max_search_ms": round(max(timings) * 1000, 3),
            "search_repeats": repeats,
            "returned_results": result_count,
        }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sizes", nargs="+", type=int, default=[10_000, 100_000])
    parser.add_argument("--repeats", type=int, default=3)
    args = parser.parse_args()
    if args.repeats < 1 or any(size < 1 for size in args.sizes):
        parser.error("sizes and repeats must be positive integers")

    print("Tamanna AI synthetic lexical retrieval benchmark")
    print(json.dumps([benchmark_size(size, args.repeats) for size in args.sizes], indent=2))


if __name__ == "__main__":
    main()
