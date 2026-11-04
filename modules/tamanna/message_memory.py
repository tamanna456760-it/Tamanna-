"""Read-only lookup for explicitly approved, local chat-memory entries.

Memory is loaded from JSON on demand. Entries are never inferred from chat logs,
and unapproved records are never returned as answers.
"""
from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any, Dict, Optional

_DEFAULT_MEMORY_PATH = Path(__file__).resolve().parents[2] / "data" / "approved_message_memory.json"
_MAX_MEMORY_BYTES = 1_000_000
_MIN_TOKEN_OVERLAP = 0.75


def _normalize(value: str) -> str:
    return " ".join(re.findall(r"[^\W_]+", value.casefold(), flags=re.UNICODE))


def _load_entries(memory_path: str | os.PathLike[str] | None = None) -> list[dict[str, Any]]:
    configured = memory_path or os.getenv("TAMANNA_MESSAGE_MEMORY_PATH")
    path = Path(configured).expanduser() if configured else _DEFAULT_MEMORY_PATH
    try:
        if not path.is_file() or path.stat().st_size > _MAX_MEMORY_BYTES:
            return []
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError, TypeError, ValueError):
        return []

    if isinstance(raw, dict):
        raw = raw.get("entries", [])
    if not isinstance(raw, list):
        return []
    return [entry for entry in raw if isinstance(entry, dict)]


def search_message_fast(
    message: str,
    memory_path: str | os.PathLike[str] | None = None,
) -> Optional[Dict[str, Any]]:
    """Return the best approved answer for an exact or strong token match.

    JSON records use: question, reply, optional category, approved=true.
    The function is intentionally read-only and returns None on invalid input,
    missing files, malformed data, or weak matches.
    """
    if not isinstance(message, str):
        return None
    query = _normalize(message)
    if not query:
        return None

    entries = _load_entries(memory_path)
    candidates: list[tuple[float, dict[str, Any]]] = []
    query_tokens = set(query.split())

    for entry in entries:
        question = entry.get("question")
        reply = entry.get("reply")
        if entry.get("approved") is not True:
            continue
        if not isinstance(question, str) or not isinstance(reply, str) or not reply.strip():
            continue
        normalized_question = _normalize(question)
        if not normalized_question:
            continue
        if normalized_question == query:
            score = 1.0
        else:
            question_tokens = set(normalized_question.split())
            if not question_tokens:
                continue
            score = len(query_tokens & question_tokens) / len(query_tokens | question_tokens)
            if score < _MIN_TOKEN_OVERLAP:
                continue
        candidates.append((score, entry))

    if not candidates:
        return None

    score, match = max(candidates, key=lambda item: item[0])
    category = match.get("category", "general")
    if not isinstance(category, str) or not category.strip():
        category = "general"
    return {
        "reply": match["reply"].strip(),
        "category": category.strip()[:80],
        "question": match["question"].strip(),
        "score": round(score, 3),
    }


__all__ = ["search_message_fast"]
