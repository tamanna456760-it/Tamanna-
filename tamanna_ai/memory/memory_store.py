"""Persistent in-memory store."""

from __future__ import annotations

from typing import Any, Dict


class MemoryStore:
    def __init__(self):
        self.store: Dict[str, Any] = {}

    def set(self, key: str, value: Any) -> None:
        self.store[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        return self.store.get(key, default)

    def all(self) -> Dict[str, Any]:
        return self.store


memory_store = MemoryStore()

__all__ = ["MemoryStore", "memory_store"]
