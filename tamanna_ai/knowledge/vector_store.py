"""Local SQLite vector store and Gemini embedding adapter for RAG.

Only explicitly imported, user-scoped text is indexed. Original documents are
never modified. The SQLite file should live on private server storage.
"""
from __future__ import annotations

import hashlib
import json
import math
import re
import sqlite3
from pathlib import Path
from contextlib import contextmanager
from typing import Iterator
from typing import Callable, Sequence

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DB = ROOT / "data" / "knowledge_vectors.sqlite3"
class EmbeddingError(RuntimeError):
    """Local embedding or vector-store error."""


class LocalFeatureEmbedder:
    """Deterministic, API-free feature-hashing embedder for local retrieval.

    This is a lightweight lexical retrieval baseline, not a trained neural
    embedding model. It hashes words and character n-grams into a fixed vector
    so the knowledge store works without hosted APIs or downloaded weights.
    """

    def __init__(self, dimensions: int = 384):
        self.dimensions = int(dimensions)
        if not 64 <= self.dimensions <= 8192:
            raise ValueError("dimensions must be between 64 and 8192")

    def __call__(
        self,
        text: str,
        task_type: str = "RETRIEVAL_DOCUMENT",
    ) -> list[float]:
        if task_type not in {"RETRIEVAL_DOCUMENT", "RETRIEVAL_QUERY"}:
            raise ValueError("Unsupported embedding task type")
        if not isinstance(text, str) or not text.strip():
            return [0.0] * self.dimensions

        tokens = re.findall(r"[^\\W_]+", text.casefold(), flags=re.UNICODE)
        features: list[tuple[str, float]] = []
        for token in tokens:
            if len(token) < 2:
                continue
            features.append(("w:" + token, 1.0))
            padded = "^" + token + "$"
            if len(padded) >= 3:
                features.extend(
                    ("c:" + padded[i:i + 3], 0.35)
                    for i in range(len(padded) - 2)
                )

        vector = [0.0] * self.dimensions
        for feature, weight in features:
            digest = hashlib.blake2b(
                feature.encode("utf-8"), digest_size=8
            ).digest()
            value = int.from_bytes(digest, "big")
            index = value % self.dimensions
            sign = 1.0 if (value >> 63) == 0 else -1.0
            vector[index] += sign * weight

        norm = math.sqrt(sum(value * value for value in vector))
        if norm:
            vector = [value / norm for value in vector]
        return vector

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
        embedder: Callable[..., list[float]] | None = None,
        db_path: str | Path = DEFAULT_DB,
        *,
        max_file_bytes: int = 10 * 1024 * 1024,
    ):
        self.embedder = embedder or LocalFeatureEmbedder()
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

    @contextmanager
    def _connect(self) -> Iterator[sqlite3.Connection]:
        connection = sqlite3.connect(self.db_path, timeout=15)
        try:
            connection.execute("PRAGMA foreign_keys=ON")
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

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
            # Replace this owner's previous version of the same source atomically.
            connection.execute(
                "DELETE FROM knowledge_chunks WHERE owner_id = ? AND source = ?",
                (owner, safe_source),
            )
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
    "EmbeddingError", "LocalFeatureEmbedder", "VectorKnowledgeStore", "chunk_text",
]
