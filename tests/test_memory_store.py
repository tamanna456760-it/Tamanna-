"""Tests for atomic JSON-backed memory persistence."""

import json

import pytest

from tamanna_ai.memory.memory_store import MemoryStore


def test_memory_store_persists_and_reloads(tmp_path):
    path = tmp_path / "private" / "memory.json"
    store = MemoryStore(path=path)
    store.set("profile", {"language": "bn", "count": 3})

    assert json.loads(path.read_text(encoding="utf-8")) == {
        "profile": {"language": "bn", "count": 3}
    }
    assert path.stat().st_mode & 0o077 == 0

    reloaded = MemoryStore(path=path)
    assert reloaded.get("profile") == {"language": "bn", "count": 3}


def test_memory_store_delete_persists(tmp_path):
    path = tmp_path / "memory.json"
    store = MemoryStore(path=path)
    store.set("temporary", "value")

    assert store.delete("temporary") is True
    assert store.delete("temporary") is False
    assert MemoryStore(path=path).all() == {}


def test_memory_store_rejects_non_json_values(tmp_path):
    store = MemoryStore(path=tmp_path / "memory.json")
    with pytest.raises(TypeError):
        store.set("bad", object())
    assert store.all() == {}


def test_memory_store_does_not_silently_reset_corrupt_file(tmp_path):
    path = tmp_path / "memory.json"
    path.write_text("{broken", encoding="utf-8")
    with pytest.raises(RuntimeError, match="Cannot load Tamanna memory file"):
        MemoryStore(path=path)
