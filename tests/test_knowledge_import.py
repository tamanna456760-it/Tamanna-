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


def test_import_redacts_bearer_jwt_and_aws_credentials(tmp_path):
    path = tmp_path / "credentials.txt"
    bearer = "Bearer " + "b" * 32
    jwt = "eyJ" + "a" * 8 + "." + "b" * 8 + "." + "c" * 8
    aws = "AKIA" + "A" * 16
    path.write_text(
        f"Authorization: {bearer} JWT={jwt} AWS={aws}",
        encoding="utf-8",
    )
    db = Database(f"sqlite:///{tmp_path / 'credentials.sqlite3'}")

    result = import_knowledge_file(path, database=db)
    assert result["imported"] == 1
    rows = search_knowledge("Authorization JWT AWS", database=db)
    assert rows
    assert bearer not in rows[0]["content"]
    assert jwt not in rows[0]["content"]
    assert aws not in rows[0]["content"]
    assert rows[0]["content"].count("[REDACTED_SECRET]") == 3


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

def test_import_rejects_invalid_utf8_without_persisting(tmp_path):
    path = tmp_path / "invalid.txt"
    path.write_bytes(b"valid prefix\xffinvalid utf8")
    db = Database(f"sqlite:///{tmp_path / 'test.sqlite3'}")

    with pytest.raises(UnicodeDecodeError):
        import_knowledge_file(path, database=db)

    assert search_knowledge("valid prefix", database=db) == []

def test_concurrent_duplicate_imports_store_only_one_record(tmp_path):
    from concurrent.futures import ThreadPoolExecutor

    path = tmp_path / "concurrent.txt"
    path.write_text("Concurrent imports must remain idempotent.", encoding="utf-8")
    db = Database(f"sqlite:///{tmp_path / 'concurrent.sqlite3'}")
    db.init()

    with ThreadPoolExecutor(max_workers=4) as executor:
        results = list(executor.map(
            lambda _: import_knowledge_file(path, database=db),
            range(4),
        ))

    assert sum(result["imported"] for result in results) == 1
    assert sum(result["skipped"] for result in results) == 3
    assert len(search_knowledge("remain idempotent", database=db)) == 1

def test_search_rejects_invalid_or_oversized_queries(tmp_path):
    db = Database(f"sqlite:///{tmp_path / 'query-limits.sqlite3'}")

    assert search_knowledge(None, database=db) == []
    assert search_knowledge(123, database=db) == []
    assert search_knowledge("x" * 2001, database=db) == []


def test_retrieval_skips_malformed_legacy_metadata(tmp_path):
    from tamanna_ai.persistence.database import Memory

    db = Database(f"sqlite:///{tmp_path / 'malformed-metadata.sqlite3'}")
    owner_id = db.ensure_user("metadata-owner@example.test", "Metadata Owner")
    with db.Session.begin() as session:
        session.add(Memory(
            user_id=owner_id,
            content="broken metadata should not break retrieval",
            metadata_json="{not valid json",
        ))
        session.add(Memory(
            user_id=owner_id,
            content="valid imported knowledge remains searchable",
            metadata_json=json.dumps({"kind": "imported_knowledge", "title": "valid"}),
        ))

    results = search_knowledge("valid imported knowledge", database=db, user_id=owner_id)
    assert len(results) == 1
    assert results[0]["title"] == "valid"


def test_anonymous_retrieval_cannot_read_user_scoped_knowledge(tmp_path):
    path = tmp_path / "owner-only.txt"
    path.write_text("Owner private retrieval boundary marker.", encoding="utf-8")
    db = Database(f"sqlite:///{tmp_path / 'test.sqlite3'}")
    owner_id = db.ensure_user("owner@example.test", "Owner")

    import_knowledge_file(path, database=db, user_id=owner_id)

    assert search_knowledge("boundary marker", database=db, user_id=owner_id)
    assert search_knowledge("boundary marker", database=db) == []

def test_export_ignores_non_string_roles(tmp_path):
    export = {"conversations": [{"title": "Role validation", "messages": [
        {"role": ["user"], "text": "invalid role content"},
        {"role": "user", "text": "valid role content"},
    ]}]}
    path = tmp_path / "roles.json"
    path.write_text(json.dumps(export), encoding="utf-8")
    db = Database(f"sqlite:///{tmp_path / 'roles.sqlite3'}")

    result = import_knowledge_file(path, database=db)

    assert result["imported"] == 1
    found = search_knowledge("valid role content", database=db)
    assert found
    assert "invalid role content" not in found[0]["content"]
