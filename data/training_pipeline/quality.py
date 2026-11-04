"""Dataset quality checks with machine-readable issue codes."""

from __future__ import annotations

from collections import Counter
from typing import Iterable


def inspect_records(records: Iterable[dict], min_chars: int = 20) -> dict:
    issues: Counter[str] = Counter()
    seen: set[str] = set()
    accepted = 0
    rejected = 0
    total = 0
    for record in records:
        total += 1
        text = str(record.get("text", ""))
        if not text.strip():
            issues["empty_text"] += 1
            rejected += 1
            continue
        if len(text.strip()) < min_chars:
            issues["too_short"] += 1
            rejected += 1
            continue
        fingerprint = text.casefold()
        if fingerprint in seen:
            issues["duplicate"] += 1
            rejected += 1
            continue
        seen.add(fingerprint)
        accepted += 1
    return {
        "total": total,
        "accepted": accepted,
        "rejected": rejected,
        "issues": dict(sorted(issues.items())),
    }
