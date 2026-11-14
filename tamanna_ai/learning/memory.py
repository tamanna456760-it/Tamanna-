"""User-scoped learning memory adapter over the canonical SQLAlchemy store."""
from __future__ import annotations

from typing import Any


class LearningMemory:
    """Store and recall explicitly approved memories for one authenticated user.

    Persistence remains in tamanna_ai.persistence; this class intentionally
    does not introduce a second database or global cross-user memory.
    """

    def __init__(self, store: Any | None = None) -> None:
        if store is None:
            from tamanna_ai.persistence.database import database
            store = database
        self.store = store

    def remember(
        self, content: str, *, user_id: int, metadata: dict[str, object] | None = None,
        deduplicate: bool = True,
    ) -> dict[str, object]:
        if user_id is None:
            raise ValueError("user_id is required")
        clean = str(content).strip()
        if not clean:
            raise ValueError("Memory content must be non-empty")
        if deduplicate:
            for row in self.store.list_memory_records(user_id=user_id, limit=500):
                if row["content"].casefold() == clean.casefold():
                    return {"status": "duplicate", "id": row["id"], "content": row["content"]}
        memory_id = self.store.add_memory(clean, user_id=user_id, metadata=metadata or {})
        return {"status": "created", "id": memory_id, "content": clean}

    def recall(self, *, user_id: int, limit: int = 100) -> list[dict[str, object]]:
        if user_id is None:
            raise ValueError("user_id is required")
        return self.store.list_memory_records(user_id=user_id, limit=limit)

    def forget(self, memory_id: int, *, user_id: int) -> bool:
        if user_id is None:
            raise ValueError("user_id is required")
        return self.store.delete_memory(memory_id, user_id=user_id)


__all__ = ["LearningMemory"]
