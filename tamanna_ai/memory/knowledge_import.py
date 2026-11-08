"""User-controlled knowledge import and retrieval for Tamanna AI.

Accepts user-owned ChatGPT exports and ordinary text/JSON/Markdown files.
It does not connect to or copy private datasets from other AI providers.
"""
from __future__ import annotations

import codecs
import hashlib
import heapq
import json
import re
import unicodedata
from pathlib import Path
from typing import Any

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from tamanna_ai.persistence.database import Database, KnowledgeFingerprint, Memory

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


def _read_bounded_text(path: Path, max_file_bytes: int) -> str:
    """Read in fixed-size blocks and reject oversized imports before persistence."""
    if max_file_bytes < 1:
        raise ValueError("max_file_bytes must be positive")
    if path.stat().st_size > max_file_bytes:
        raise ValueError("Import exceeds the configured file size limit")
    decoder = codecs.getincrementaldecoder("utf-8")(errors="strict")
    parts: list[str] = []
    total = 0
    with path.open("rb") as stream:
        while True:
            block = stream.read(64 * 1024)
            if not block:
                break
            total += len(block)
            if total > max_file_bytes:
                raise ValueError("Import exceeds the configured file size limit")
            parts.append(decoder.decode(block))
    parts.append(decoder.decode(b"", final=True))
    return "".join(parts)


def import_knowledge_file(
    file_path: str | Path,
    *,
    database: Database,
    user_id: int | None = None,
    source_label: str | None = None,
    max_file_bytes: int = 10 * 1024 * 1024,
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
    raw_file = _read_bounded_text(path, int(max_file_bytes))
    if path.suffix.lower() == ".json":
        data = json.loads(raw_file)
        records = _chatgpt_export_records(data)
        if not records:
            serialized = json.dumps(data, ensure_ascii=False, indent=2)
            records = [(path.stem, serialized)]
    else:
        records = [(path.stem, raw_file)]

    database.init()
    imported = skipped = 0
    source = (source_label or path.name)[:255]
    with database.Session.begin() as session:
        # Read legacy hashes once, rather than issuing one full-table query per record.
        existing_hashes: set[str] = set()
        legacy_rows = session.scalars(
            select(Memory.metadata_json).where(Memory.user_id == user_id)
        )
        for metadata_json in legacy_rows:
            try:
                legacy_hash = json.loads(metadata_json or "{}").get("sha256")
                if isinstance(legacy_hash, str):
                    existing_hashes.add(legacy_hash)
            except (TypeError, json.JSONDecodeError):
                continue
        for title, raw_text in records:
            text = _redact_secrets(raw_text).strip()
            if not text:
                skipped += 1
                continue
            digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
            scope = "anonymous" if user_id is None else str(user_id)
            fingerprint = hashlib.sha256(f"{scope}:{digest}".encode("utf-8")).hexdigest()
            if digest in existing_hashes:
                skipped += 1
                continue
            metadata = {
                "kind": "imported_knowledge",
                "source": source,
                "title": title[:200],
                "sha256": digest,
                "trust": "user_supplied_unverified",
            }
            try:
                # The primary key prevents duplicate writes even if two imports race.
                with session.begin_nested():
                    session.add(KnowledgeFingerprint(fingerprint=fingerprint))
                    session.flush()
                    session.add(Memory(
                        user_id=user_id,
                        content=text,
                        metadata_json=json.dumps(metadata, ensure_ascii=False, sort_keys=True),
                    ))
                imported += 1
                existing_hashes.add(digest)
            except IntegrityError as exc:
                # Only treat a duplicate idempotency key as a harmless repeat.
                # Foreign-key and other integrity failures must surface to the caller.
                error_text = str(exc.orig).lower()
                duplicate_fingerprint = (
                    "knowledge_fingerprints" in error_text
                    and ("unique constraint" in error_text or "duplicate key" in error_text)
                )
                if not duplicate_fingerprint:
                    raise
                skipped += 1
    return {"status": "ok", "imported": imported, "skipped": skipped, "source": source}


def search_knowledge(
    query: str,
    *,
    database: Database,
    user_id: int | None = None,
    limit: int = 5,
) -> list[dict[str, str]]:
    """Small dependency-free lexical retrieval; callers must enforce user auth."""
    # Python's default \w is not Unicode-letter complete (for example, it
    # misses Bengali letters). Tokenize by Unicode character categories.
    tokens: list[str] = []
    current: list[str] = []
    for character in query.casefold():
        category = unicodedata.category(character)
        if category[0] in {"L", "N"} or character in "_-":
            current.append(character)
        elif current:
            token = "".join(current)
            if 2 <= len(token) < 80:
                tokens.append(token)
            current = []
    if current:
        token = "".join(current)
        if 2 <= len(token) < 80:
            tokens.append(token)
    terms = set(tokens)
    if not terms:
        return []
    limit = max(1, min(int(limit), 20))
    database.init()
    # Restrict SQL rows to one owner (or anonymous imports), then stream in batches.
    # A bounded min-heap keeps top-k ranking O(n log k), avoiding a full sort per hit.
    ranked: list[tuple[int, Any, int, str, dict[str, Any]]] = []
    with database.Session() as session:
        statement = select(Memory).order_by(Memory.id)
        if user_id is None:
            statement = statement.where(Memory.user_id.is_(None))
        else:
            statement = statement.where(Memory.user_id == user_id)
        for row in session.scalars(statement).yield_per(500):
            metadata = json.loads(row.metadata_json or "{}")
            if metadata.get("kind") != "imported_knowledge":
                continue
            haystack = row.content.casefold()
            score = sum(1 for term in terms if term in haystack)
            if score:
                item = (score, row.created_at, row.id, row.content, metadata)
                if len(ranked) < limit:
                    heapq.heappush(ranked, item)
                elif item[:3] > ranked[0][:3]:
                    heapq.heapreplace(ranked, item)
    ranked.sort(key=lambda item: (item[0], item[1], item[2]), reverse=True)
    return [
        {"content": content, "source": str(metadata.get("source", "unknown")), "title": str(metadata.get("title", ""))}
        for _, _, _, content, metadata in ranked
    ]


__all__ = ["import_knowledge_file", "search_knowledge"]
