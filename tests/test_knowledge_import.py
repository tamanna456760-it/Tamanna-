from __future__ import annotations

import json

import pytest

from tamanna_ai.persistence.database import Database
from tamanna_ai.memory.knowledge_import import import_knowledge_file, search_knowledge


def test_import_chatgpt_export_and_retrieve(tmp_path):
    export = {
        "conversations": [{
            "title": "Tamanna project",
            "mapping": {
                "a": {"message": {"author": {"role": "user"}, "content": {"parts": ["Build a secure memory system"]}}},
                "b": {"message": {"author": {"role": "assistant"}, "content": {"parts": ["Use source citations and access control"]}}},
            },
        }]
    }
    path = tmp_path / "conversations.json"
    path.write_text(json.dumps(export), encoding="utf-8")
    db = Database(f"sqlite:///{tmp_path / 'test.sqlite3'}")
    user_id = db.ensure_user("memory-test@example.test", "Memory Test")

    result = import_knowledge_file(path, database=db, user_id=user_id)
    assert result["imported"] == 1
    found = search_knowledge("source citations", database=db, user_id=user_id)
    assert found and found[0]["title"] == "Tamanna project"
    assert search_knowledge("source citations", database=db, user_id=user_id + 1) == []


def test_import_is_idempotent_and_redacts_secrets(tmp_path):
    path = tmp_path / "notes.txt"
    path.write_text("Remember this API_KEY=supersecretvalue and secure backups.", encoding="utf-8")
    db = Database(f"sqlite:///{tmp_path / 'test.sqlite3'}")

    first = import_knowledge_file(path, database=db)
    second = import_knowledge_file(path, database=db)
    assert first["imported"] == 1
    assert second["imported"] == 0
    rows = search_knowledge("secure backups", database=db)
    assert rows
    assert "supersecretvalue" not in rows[0]["content"]
    assert "[REDACTED_SECRET]" in rows[0]["content"]


def test_reject_unsupported_or_oversized_file(tmp_path):
    db = Database(f"sqlite:///{tmp_path / 'test.sqlite3'}")
    unsupported = tmp_path / "dump.bin"
    unsupported.write_bytes(b"x")
    with pytest.raises(ValueError):
        import_knowledge_file(unsupported, database=db)

    oversized = tmp_path / "large.txt"
    oversized.write_text("x" * 32, encoding="utf-8")
    with pytest.raises(ValueError, match="size limit"):
        import_knowledge_file(oversized, database=db, max_file_bytes=16)
def test_import_handles_utf8_character_split_across_read_blocks(tmp_path):
    path = tmp_path / "utf8-boundary.txt"
    path.write_text("x" * 65535 + "বাংলা knowledge boundary test", encoding="utf-8")
    db = Database(f"sqlite:///{tmp_path / 'test.sqlite3'}")

    result = import_knowledge_file(path, database=db)

    assert result["imported"] == 1
    found = search_knowledge("বাংলা", database=db)
    assert found and "বাংলা" in found[0]["content"]
def test_duplicate_fingerprints_are_scoped_per_user(tmp_path):
    path = tmp_path / "shared.txt"
    path.write_text("Private knowledge must remain tenant isolated.", encoding="utf-8")
    db = Database(f"sqlite:///{tmp_path / 'test.sqlite3'}")
    first_user = db.ensure_user("first@example.test", "First")
    second_user = db.ensure_user("second@example.test", "Second")

    first = import_knowledge_file(path, database=db, user_id=first_user)
    repeat = import_knowledge_file(path, database=db, user_id=first_user)
    second = import_knowledge_file(path, database=db, user_id=second_user)

    assert first["imported"] == 1
    assert repeat["imported"] == 0
    assert second["imported"] == 1
    assert search_knowledge("tenant isolated", database=db, user_id=first_user)
    assert search_knowledge("tenant isolated", database=db, user_id=second_user)
