"""Offline training-data inspection; this module does not train model weights."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def inspect_jsonl_dataset(path: str | Path, *, max_line_bytes: int = 1_000_000) -> dict[str, Any]:
    """Validate JSONL chat records and report counts without modifying the input."""
    source = Path(path)
    accepted = 0
    rejected = 0
    duplicates = 0
    seen: set[str] = set()
    issues: list[dict[str, Any]] = []
    with source.open("rb") as stream:
        for line_number, raw in enumerate(stream, start=1):
            if not raw.strip():
                continue
            if len(raw) > max_line_bytes:
                rejected += 1
                issues.append({"line": line_number, "reason": "line_too_large"})
                continue
            try:
                row = json.loads(raw.decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError):
                rejected += 1
                issues.append({"line": line_number, "reason": "invalid_json"})
                continue
            messages = row.get("messages") if isinstance(row, dict) else None
            if not isinstance(messages, list) or len(messages) < 2:
                rejected += 1
                issues.append({"line": line_number, "reason": "messages_required"})
                continue
            valid = (
                messages[0].get("role") == "user"
                and messages[-1].get("role") == "assistant"
                and all(isinstance(item, dict) and isinstance(item.get("content"), str) and item["content"].strip() for item in messages)
            )
            if not valid:
                rejected += 1
                issues.append({"line": line_number, "reason": "invalid_chat_messages"})
                continue
            fingerprint = json.dumps(messages, ensure_ascii=False, sort_keys=True)
            if fingerprint in seen:
                duplicates += 1
                rejected += 1
                issues.append({"line": line_number, "reason": "duplicate"})
                continue
            seen.add(fingerprint)
            accepted += 1
    return {
        "status": "ok",
        "source": str(source),
        "accepted": accepted,
        "rejected": rejected,
        "duplicates": duplicates,
        "issues": issues,
        "model_training_performed": False,
    }


__all__ = ["inspect_jsonl_dataset"]
