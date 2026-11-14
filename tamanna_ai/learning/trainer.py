"""Offline training-data inspection; this module does not train model weights."""
from __future__ import annotations
import json
from pathlib import Path
from typing import Any

def inspect_jsonl_dataset(path: str | Path, *, max_line_bytes: int = 1_000_000) -> dict[str, Any]:
    """Validate JSONL chat records and report counts without modifying the input."""
    if max_line_bytes < 1:
        raise ValueError("max_line_bytes must be positive")
    source = Path(path)
    accepted = rejected = duplicates = 0
    seen: set[str] = set()
    issues: list[dict[str, Any]] = []
    with source.open("rb") as stream:
        for line_number, raw in enumerate(stream, start=1):
            if not raw.strip():
                continue
            reason = None
            if len(raw) > max_line_bytes:
                reason = "line_too_large"
            else:
                try:
                    row = json.loads(raw.decode("utf-8"))
                except (UnicodeDecodeError, json.JSONDecodeError):
                    reason = "invalid_json"
                else:
                    messages = row.get("messages") if isinstance(row, dict) else None
                    if not isinstance(messages, list) or len(messages) < 2:
                        reason = "messages_required"
                    elif not all(isinstance(item, dict) for item in messages):
                        reason = "invalid_chat_messages"
                    elif (messages[0].get("role") != "user" or messages[-1].get("role") != "assistant"
                          or not all(isinstance(item.get("content"), str) and item["content"].strip() for item in messages)):
                        reason = "invalid_chat_messages"
                    else:
                        fingerprint = json.dumps(messages, ensure_ascii=False, sort_keys=True)
                        if fingerprint in seen:
                            duplicates += 1
                            reason = "duplicate"
                        else:
                            seen.add(fingerprint)
            if reason:
                rejected += 1
                issues.append({"line": line_number, "reason": reason})
            else:
                accepted += 1
    return {"status": "ok", "source": str(source), "accepted": accepted, "rejected": rejected,
            "duplicates": duplicates, "issues": issues, "model_training_performed": False}

__all__ = ["inspect_jsonl_dataset"]
