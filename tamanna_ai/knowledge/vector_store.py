"""Local SQLite vector store and Gemini embedding adapter for RAG.

Only explicitly imported, user-scoped text is indexed. Original documents are
never modified. The SQLite file should live on private server storage.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import re
import sqlite3
from pathlib import Path
from typing import Callable, Sequence

import httpx

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DB = ROOT / "data" / "knowledge_vectors.sqlite3"
EMBEDDING_MODEL = "gemini-embedding-001"
EMBEDDING_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    + EMBEDDING_MODEL + ":embedContent"
)


class EmbeddingError(RuntimeError):
    """Embedding provider configuration or request failed."""


class GeminiEmbedder:
    """Generate retrieval embeddings with Google's Gemini embedding API."""

    def __init__(self, api_key: str | None = None, timeout: float = 20.0):
        self.api_key = (api_key or os.getenv("GEMINI_API_KEY", "")).strip()
        self.timeout = float(timeout)
        if self.timeout <= 0:
            raise ValueError("timeout must be positive")

    def __call__(self, text: str, task_type: str = "RETRIEVAL_DOCUMENT") -> list[float]:
        if not self.api_key:
            raise EmbeddingError("GEMINI_API_KEY is not configured")
        if task_type not in {"RETRIEVAL_DOCUMENT", "RETRIEVAL_QUERY"}:
            raise ValueError("Unsupported embedding task type")
        payload = {
            "model": "models/" + EMBEDDING_MODEL,
            "content": {"parts": [{"text": text[:10000]}]},
            "taskType": task_type,
        }
        try:
            response = httpx.post(
                EMBEDDING_URL,
                headers={"x-goog-api-key": self.api_key},
                json=payload,
                timeout=self.timeout,
            )
            response.raise_for_status()
            values = response.json()["embedding"]["values"]
        except (httpx.HTTPError, ValueError, KeyError, TypeError) as exc:
            raise EmbeddingError("Gemini embedding request failed") from exc
        if not isinstance(values, list) or not values or any(
            not isinstance(value, (int, float)) or not math.isfinite(value)
            for value in values
        ):
            raise EmbeddingError("Gemini returned an invalid embedding vector")
        return [float(value) for value in values]


def chunk_text(text: str, *, max_chars: int = 1200, overlap: int = 150) -> list[str]:
    """Split text into bounded overlapping chunks, preferring paragraph boundaries."""
    if not isinstance(text, str) or not text.strip():
        return []
    if max_chars < 100 or overlap < 0 or overlap >= max_chars:
        raise ValueError("Invalid chunk size or overlap")
    paragraphs = [part.strip() for part in re.split(r"\n\s*\n", text) if part.strip()]
    chunks: list[str] = []
    current = ""
    for paragraph in paragraphs:
        while len(paragraph) > max_chars:
            piece, paragraph = paragraph[:max_chars], paragraph[max_chars - overlap:]
            if current:
                chunks.append(current)
                current = ""
            chunks.append(piece)
        candidate = (current + "\n\n" + paragraph).strip() if current else paragraph
        if len(candidate) <= max_chars:
            current = candidate
        else:
            chunks.append(current)
            current = (current[-overlap:] + "\n" + paragraph).strip() if overlap else paragraph
    if current:
        chunks.append(current)
    return chunks


def _cosine(left: Sequence[float], right: Sequence[float]) -> float:
    if len(left) != len(right) or not left:
        return -1.0
    dot = sum(a * b for a, b in zip(left, right))
    left_norm = math.sqrt(sum(a * a for a in left))
    right_norm = math.sqrt(sum(b * b for b in right))
    return dot / (left_norm * right_norm) if left_norm and right_norm else -1.0


class VectorKnowledgeStore:
    """Persistent, owner-isolated vector index using SQLite and an embedder callable."""

    def __init__(
        self,
        embedder: Callable[..., list[float]],
        db_path: str | Path = DEFAULT_DB,
        *,
        max_file_bytes: int = 10 * 1024 * 1024,
    ):
        self.embedder = embedder
        self.db_path = Path(db_path)
        self.max_file_bytes = max(1024, int(max_file_bytes))
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as connection:
            connection.execute("""
                CREATE TABLE IF NOT EXISTS knowledge_chunks (
                    chunk_id TEXT PRIMARY KEY,
                    owner_id TEXT NOT NULL,
                    source TEXT NOT NULL,
                    title TEXT NOT NULL,
                    chunk_text TEXT NOT NULL,
                    embedding_json TEXT NOT NULL,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
            """)
            connection.execute(
                "CREATE INDEX IF NOT EXISTS idx_knowledge_owner ON knowledge_chunks(owner_id)"
            )

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.db_path, timeout=15)
        connection.execute("PRAGMA foreign_keys=ON")
        return connection

    def index_text(self, text: str, *, owner_id: str, source: str, title: str = "") -> int:
        owner = str(owner_id).strip()
        if not owner:
            raise ValueError("owner_id is required to isolate private knowledge")
        if not isinstance(text, str) or not text.strip():
            return 0
        if len(text.encode("utf-8")) > self.max_file_bytes:
            raise ValueError("Document exceeds the configured size limit")
        safe_source = str(source).strip()[:500]
        if not safe_source:
            raise ValueError("source is required")
        pieces = chunk_text(text)
        prepared = []
        for index, piece in enumerate(pieces):
            vector = self.embedder(piece, task_type="RETRIEVAL_DOCUMENT")
            if not vector:
                raise EmbeddingError("Embedder returned an empty vector")
            chunk_id = hashlib.sha256(
                f"{owner}\0{safe_source}\0{index}\0{piece}".encode("utf-8")
            ).hexdigest()
            prepared.append((
                chunk_id, owner, safe_source, str(title)[:200], piece,
                json.dumps(vector, separators=(",", ":")),
            ))
        with self._connect() as connection:
            connection.executemany("""
                INSERT INTO knowledge_chunks
                (chunk_id, owner_id, source, title, chunk_text, embedding_json)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(chunk_id) DO UPDATE SET
                    title=excluded.title, chunk_text=excluded.chunk_text,
                    embedding_json=excluded.embedding_json
            """, prepared)
        return len(prepared)

    def index_document(self, file_path: str | Path, *, owner_id: str) -> int:
        """Extract text from an approved local document and add its chunks."""
        from .document_loader import load_document_text

        path = Path(file_path)
        text = load_document_text(path, max_bytes=self.max_file_bytes)
        return self.index_text(
            text, owner_id=owner_id, source=path.name, title=path.stem
        )

    def search(self, query: str, *, owner_id: str, limit: int = 5) -> list[dict[str, object]]:
        owner = str(owner_id).strip()
        if not owner:
            raise ValueError("owner_id is required to retrieve private knowledge")
        if not isinstance(query, str) or not query.strip():
            return []
        limit = max(1, min(int(limit), 20))
        query_vector = self.embedder(query.strip()[:10000], task_type="RETRIEVAL_QUERY")
        with self._connect() as connection:
            rows = connection.execute("""
                SELECT source, title, chunk_text, embedding_json
                FROM knowledge_chunks WHERE owner_id = ?
            """, (owner,)).fetchall()
        ranked = []
        for source, title, chunk, vector_json in rows:
            score = _cosine(query_vector, json.loads(vector_json))
            if score >= 0:
                ranked.append((score, source, title, chunk))
        ranked.sort(key=lambda item: item[0], reverse=True)
        return [
            {"score": score, "source": source, "title": title, "content": chunk}
            for score, source, title, chunk in ranked[:limit]
        ]

    def delete_source(self, source: str, *, owner_id: str) -> int:
        owner = str(owner_id).strip()
        if not owner:
            raise ValueError("owner_id is required to delete private knowledge")
        with self._connect() as connection:
            cursor = connection.execute(
                "DELETE FROM knowledge_chunks WHERE owner_id = ? AND source = ?",
                (owner, str(source)),
            )
            return cursor.rowcount


__all__ = [
    "EmbeddingError", "GeminiEmbedder", "VectorKnowledgeStore", "chunk_text",
]
