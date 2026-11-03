"""Safe, repeatable synthetic knowledge-memory load benchmark.

Defaults to 10,000 unique records in a temporary SQLite database. It never
uses Tamanna's configured/production database and never commits generated data.
"""
from __future__ import annotations

import argparse
import json
import tempfile
import time
from pathlib import Path

from sqlalchemy import func, select

from tamanna_ai.memory.knowledge_import import import_knowledge_file, search_knowledge
from tamanna_ai.persistence.database import Database, Memory


TOPICS = (
    "python programming", "database indexing", "network security",
    "machine learning", "linear algebra", "astronomy", "world geography",
    "climate science", "history research", "language learning",
)


def build_export(start: int, count: int) -> dict:
    conversations = []
    for number in range(start, start + count):
        topic = TOPICS[number % len(TOPICS)]
        conversations.append({
            "title": f"Load test {number:06d} - {topic}",
            "messages": [
                {"role": "user", "content": f"Explain {topic}, benchmark record {number:06d}."},
                {"role": "assistant", "content": (
                    f"Synthetic test fact {number:06d}: {topic} is stored as a "
                    "separate searchable knowledge record. This is generated "
                    "benchmark data, not a real-world factual claim."
                )},
            ],
        })
    return {"conversations": conversations}


def count_imported(database: Database) -> int:
    with database.Session() as session:
        return int(session.scalar(
            select(func.count()).select_from(Memory).where(
                Memory.metadata_json.like('%"kind": "imported_knowledge"%')
            )
        ) or 0)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--records", type=int, default=10_000)
    parser.add_argument("--batch-size", type=int, default=1_000)
    args = parser.parse_args()
    if not 1 <= args.records <= 100_000:
        parser.error("--records must be between 1 and 100000")
    if not 1 <= args.batch_size <= 2_000:
        parser.error("--batch-size must be between 1 and 2000")

    with tempfile.TemporaryDirectory(prefix="tamanna-memory-benchmark-") as temp:
        root = Path(temp)
        database = Database(f"sqlite:///{root / 'benchmark.sqlite3'}")
        database.init()
        started = time.perf_counter()
        first_imported = first_skipped = batches = 0

        for start in range(0, args.records, args.batch_size):
            count = min(args.batch_size, args.records - start)
            source = root / f"batch-{start:06d}.json"
            source.write_text(
                json.dumps(build_export(start, count), ensure_ascii=False),
                encoding="utf-8",
            )
            result = import_knowledge_file(source, database=database, user_id=1)
            first_imported += result["imported"]
            first_skipped += result["skipped"]
            batches += 1

        first_seconds = time.perf_counter() - started
        stored_after_first = count_imported(database)

        duplicate_started = time.perf_counter()
        second_imported = second_skipped = 0
        for start in range(0, args.records, args.batch_size):
            source = root / f"batch-{start:06d}.json"
            result = import_knowledge_file(source, database=database, user_id=1)
            second_imported += result["imported"]
            second_skipped += result["skipped"]
        duplicate_seconds = time.perf_counter() - duplicate_started
        stored_after_second = count_imported(database)

        retrieval = search_knowledge(
            f"synthetic test fact {args.records - 1:06d}",
            database=database,
            user_id=1,
            limit=5,
        )
        retrieval_hit = any(
            f"{args.records - 1:06d}" in item["content"] for item in retrieval
        )

        passed = (
            first_imported == args.records
            and first_skipped == 0
            and stored_after_first == args.records
            and second_imported == 0
            and second_skipped == args.records
            and stored_after_second == args.records
            and retrieval_hit
        )
        print(json.dumps({
            "status": "PASS" if passed else "FAIL",
            "target_records": args.records,
            "batch_size": args.batch_size,
            "batches": batches,
            "first_imported": first_imported,
            "first_skipped": first_skipped,
            "stored_after_first_import": stored_after_first,
            "second_imported": second_imported,
            "second_skipped_as_duplicates": second_skipped,
            "stored_after_second_import": stored_after_second,
            "first_import_seconds": round(first_seconds, 3),
            "duplicate_pass_seconds": round(duplicate_seconds, 3),
            "retrieval_hit_for_last_record": retrieval_hit,
            "database": "temporary SQLite (deleted automatically)",
        }, indent=2))
        return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
