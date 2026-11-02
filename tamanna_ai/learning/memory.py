"""Compatibility facade for learning-related memory access.

This module records and retrieves explicit learning notes; it does not train
model weights or silently collect user data.
"""

from __future__ import annotations

from typing import Any

from ..memory.memory import forget, recall, recall_all, remember


def record_learning_note(key: str, value: Any) -> dict[str, Any]:
    """Store one caller-supplied learning note in Tamanna's memory store."""
    return remember(key, value)


def get_learning_note(key: str, default: Any = None) -> Any:
    """Retrieve a note without changing the stored value."""
    return recall(key, default)


def list_learning_notes() -> dict[str, Any]:
    """Return a shallow snapshot of all stored learning notes."""
    return dict(recall_all())


def delete_learning_note(key: str) -> bool:
    """Delete a note by key."""
    return forget(key)


__all__ = [
    "record_learning_note",
    "get_learning_note",
    "list_learning_notes",
    "delete_learning_note",
]
