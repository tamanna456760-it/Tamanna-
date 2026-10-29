
"""Compatibility helpers for Tamanna AI memory."""

from __future__ import annotations

from typing import Any

from .memory_store import memory_store


def remember(key: str, value: Any) -> dict[str, Any]:
    key = str(key).strip()
    if not key:
        return {"ok": False, "error": "memory_key_required"}

    memory_store.set(key, value)
    return {"ok": True, "key": key}


def recall(key: str, default: Any = None) -> Any:
    return memory_store.get(str(key), default)


def recall_all() -> dict[str, Any]:
    return memory_store.all()


def forget(key: str) -> bool:
    key = str(key).strip()
    if not key:
        return False
    return memory_store.store.pop(key, None) is not None


__all__ = ["remember", "recall", "recall_all", "forget"]
