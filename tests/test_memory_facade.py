"""Tests for the learning-memory compatibility facade."""

from tamanna_ai.learning.memory import (
    delete_learning_note,
    get_learning_note,
    list_learning_notes,
    record_learning_note,
)


def test_learning_memory_round_trip():
    key = "pytest-learning-memory-round-trip"
    try:
        result = record_learning_note(key, {"approved": True, "note": "sample"})
        assert result == {"ok": True, "key": key}
        assert get_learning_note(key) == {"approved": True, "note": "sample"}
        assert list_learning_notes()[key] == {"approved": True, "note": "sample"}
    finally:
        delete_learning_note(key)
    assert get_learning_note(key) is None
