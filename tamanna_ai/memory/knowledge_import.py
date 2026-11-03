"""User-controlled knowledge import and retrieval for Tamanna AI.

Accepts user-owned ChatGPT exports and ordinary text/JSON/Markdown files.
It does not connect to or copy private datasets from other AI providers.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

from sqlalchemy import select

from tamanna_ai.persistence.database import Database, Memory

MAX_FILE_BYTES = 20 * 1024 * 1024
MAX_TEXT_CHARS = 100_000
_SECRET_PATTERNS = (
    re.compile(r"(?i)\b(api[_-]?key|access[_-]?token|client[_-]?secret|password)\s*[:=]\s*[^\s,;]+"),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b"),
    re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
)


def _redact_secrets(text: str) -> str:
    for pattern in _SECRET_PATTERNS:
        text = pattern.sub("[REDACTED_SECRET]", text)
    return text


def _plain_text(value: Any) -> str:
    """Extract readable text from common ChatGPT export message structures."""
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        return "\n".join(part for item in value if (part := _plain_text(item)))
    if isinstance(value, dict):
        if isinstance(value.get("text"), str):
            return value["text"]
        if isinstance(value.get("parts"), list):
            return _plain_text(value["parts"])
        if isinstance(value.get("content"), (str, list, dict)):
            return _plain_text(value["content"])
    return ""


def _chatgpt_export_records(data: Any) -> list[tuple[str, str]]:
    conversations = data if isinstance(data, list) else data.get("conversations", []) if isinstance(data, dict) else []
    records: list[tuple[str, str]] = []
    if not isinstance(conversations, list):
        return records
    for conversation in conversations:
        if not isinstance(conversation, dict):
            continue
        title = str(conversation.get("title") or "Imported conversation")[:200]
        mapping = conversation.get("mapping")
        messages = []
        if isinstance(mapping, dict):
            for node in mapping.values():
                message = node.get("message") if isinstance(node, dict) else None
                if not isinstance(message, dict):
                    continue
                author = message.get("author") or {}
                role = author.get("role", "unknown") if isinstance(author, dict) else "unknown"
                text = _plain_text(message.get("content"))
                if role in {"user", "assistant"} and text.strip():
                    messages.append(f"{role}: {text.strip()}")
        if not messages and isinstance(conversation.get("messages"), list):
            for message in conversation["messages"]:
                if isinstance(message, dict):
                    role = message.get("role", "unknown")
                    text = _plain_text(message.get("content") or message.get("text"))
                    if role in {"user", "assistant"} and text.strip():
                        messages.append(f"{role}: {text.strip()}")
        if messages:
            records.append((title, "\n\n".join(messages)))
    return records


def import_knowledge_file(
    file_path: str | Path,
    *,
    database: Database,
    user_id: int | None = None,
    source_label: str | None = None,
) -> dict[str, Any]:
    """Explicitly import a user-selected .json, .txt, or .md file.

    Original files are never modified. Sensitive credential-like strings are
    redacted before persistence. Each imported record stores source provenance
    and a content hash so repeat imports are idempotent.
    """
    path = Path(file_path)
    if path.suffix.lower() not in {".json", ".txt", ".md"}:
        raise ValueError("Supported formats are .json, .txt, and .md")
    if not path.is_file():
        raise FileNotFoundError(path)
    if path.stat().st_size > MAX_FILE_BYTES:
        raise ValueError("Import file exceeds the 20 MiB limit")

    if path.suffix.lower() == ".json":
        data = json.loads(path.read_text(encoding="utf-8"))
        records = _chatgpt_export_records(data)
        if not records:
            serialized = json.dumps(data, ensure_ascii=False, indent=2)
            records = [(path.stem, serialized)]
    else:
        records = [(path.stem, path.read_text(encoding="utf-8"))]

    database.init()
    imported = skipped = 0
    source = (source_label or path.name)[:255]
    with database.Session.begin() as session:
        for title, raw_text in records:
            text = _redact_secrets(raw_text).strip()[:MAX_TEXT_CHARS]
            if not text:
                skipped += 1
                continue
            digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
            duplicate = session.scalar(
                select(Memory.id).where(Memory.user_id == user_id, Memory.metadata_json.like(f'%"sha256": "{digest}"%')).limit(1)
            )
            if duplicate is not None:
                skipped += 1
                continue
            metadata = {
                "kind": "imported_knowledge",
                "source": source,
                "title": title[:200],
                "sha256": digest,
                "trust": "user_supplied_unverified",
            }
            session.add(Memory(
                user_id=user_id,
                content=text,
                metadata_json=json.dumps(metadata, ensure_ascii=False, sort_keys=True),
            ))
            imported += 1
    return {"status": "ok", "imported": imported, "skipped": skipped, "source": source}


def search_knowledge(
    query: str,
    *,
    database: Database,
    user_id: int | None = None,
    limit: int = 5,
) -> list[dict[str, str]]:
    """Small dependency-free lexical retrieval; callers must enforce user auth."""
    terms = {term.lower() for term in re.findall(r"[\w-]{2,}", query) if len(term) < 80}
    if not terms:
        return []
    limit = max(1, min(int(limit), 20))
    with database.Session() as session:
        statement = select(Memory)
        if user_id is not None:
            statement = statement.where(Memory.user_id == user_id)
        rows = list(session.scalars(statement.order_by(Memory.created_at.desc()).limit(1000)))
    ranked = []
    for row in rows:
        metadata = json.loads(row.metadata_json or "{}")
        if metadata.get("kind") != "imported_knowledge":
            continue
        haystack = row.content.lower()
        score = sum(1 for term in terms if term in haystack)
        if score:
            ranked.append((score, row, metadata))
    ranked.sort(key=lambda item: (item[0], item[1].created_at), reverse=True)
    return [
        {"content": row.content, "source": str(metadata.get("source", "unknown")), "title": str(metadata.get("title", ""))}
        for _, row, metadata in ranked[:limit]
    ]


__all__ = ["import_knowledge_file", "search_knowledge"]
