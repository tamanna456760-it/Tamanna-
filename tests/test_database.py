"""Tests for SQLAlchemy chat persistence and safe legacy migration."""
import json
import pytest
from pathlib import Path
from sqlalchemy import inspect

from tamanna_ai.persistence.database import Database, Memory, User


def test_database_creates_required_tables_and_saves_chat(tmp_path):
    db = Database("sqlite:///" + (tmp_path / "chat.sqlite3").as_posix())
    db.init()
    user_id = db.ensure_user("chat-owner@example.test", "Chat Owner")
    db.save_chat_pair("hello", "hi there", user_id=user_id)
    history = db.load_history(user_id=user_id)
    assert len(history) == 1
    assert history[0]["user"] == "hello"
    assert history[0]["assistant"] == "hi there"
    assert {"users", "conversations", "messages", "memories"}.issubset(
        set(inspect(db.engine).get_table_names())
    )


def test_legacy_json_is_backed_up_before_import(tmp_path):
    db = Database("sqlite:///" + (tmp_path / "chat.sqlite3").as_posix())
    db.init()
    old = tmp_path / "chat_history.json"
    old.write_text(json.dumps([{
        "time": "2026-01-01T00:00:00",
        "user": "old question",
        "assistant": "old answer",
    }]), encoding="utf-8")

    result = db.migrate_legacy_json(old)
    assert result["status"] == "migrated"
    assert result["imported"] == 1
    backup = result["backup"]
    assert backup and Path(backup).read_text(encoding="utf-8") == old.read_text(encoding="utf-8")
    # Legacy imports have no verified account owner and must stay private.
    assert db.load_history("legacy-import", user_id=None) == []
    assert db.migrate_legacy_json(old)["status"] == "already_migrated"


def test_memory_table_accepts_persistent_records(tmp_path):
    db = Database("sqlite:///" + (tmp_path / "memory.sqlite3").as_posix())
    db.init()
    with db.Session.begin() as session:
        user = User(email="test@example.com", name="Test")
        session.add(user)
        session.flush()
        session.add(Memory(user_id=user.id, content="remember this", metadata_json='{"source":"test"}'))
    with db.Session() as session:
        assert session.query(Memory).one().content == "remember this"
        assert session.query(User).one().email == "test@example.com"



def test_database_memory_api_persists_and_lists_memories(tmp_path):
    db = Database("sqlite:///" + (tmp_path / "persistent-memory.sqlite3").as_posix())
    user_id = db.ensure_user("memory-owner@example.test", "Memory Owner")
    memory_id = db.add_memory("keep this", user_id=user_id, metadata={"source": "test"})
    assert memory_id > 0
    assert db.list_memories(user_id=user_id) == ["keep this"]
    assert db.list_memories(user_id=None) == []



def test_conversation_history_is_scoped_to_user_and_rejects_cross_user_write(tmp_path):
    db = Database("sqlite:///" + (tmp_path / "user-history.sqlite3").as_posix())
    first = db.ensure_user("first@example.test", "First")
    second = db.ensure_user("second@example.test", "Second")
    db.save_chat_pair("first question", "first answer", f"user-{first}", first)
    db.save_chat_pair("second question", "second answer", f"user-{second}", second)

    assert [row["user"] for row in db.load_history(user_id=first)] == ["first question"]
    assert [row["user"] for row in db.load_history(user_id=second)] == ["second question"]
    with pytest.raises(PermissionError):
        db.save_chat_pair("intrusion", "no", f"user-{first}", second)


def test_benchmark_history_persists_recent_model_metrics_without_prompt_content(tmp_path):
    db = Database("sqlite:///" + (tmp_path / "benchmark.sqlite3").as_posix())
    first = {
        "wall_time_ms": 321.5,
        "passed_checks": 2,
        "total_checks": 3,
        "generation_tokens_per_second": 18.4,
    }
    second = {
        "wall_time_ms": 280.0,
        "passed_checks": 3,
        "total_checks": 3,
        "generation_tokens_per_second": 21.2,
    }

    first_id = db.save_benchmark_run(model="qwen2.5:7b", result=first)
    second_id = db.save_benchmark_run(model="llama3.2:3b", result=second)
    history = db.list_benchmark_runs(limit=1)
    assert len(history) == 1
    assert history[0]["id"] == second_id
    assert history[0]["model"] == "llama3.2:3b"
    assert history[0]["result"] == second
    assert second_id > first_id
    assert "prompt" not in str(history[0]).lower()


def test_benchmark_history_limit_is_bounded(tmp_path):
    db = Database("sqlite:///" + (tmp_path / "benchmark-limit.sqlite3").as_posix())
    for index in range(3):
        db.save_benchmark_run(model="local-test", result={"index": index})
    assert len(db.list_benchmark_runs(limit=0)) == 1
    assert len(db.list_benchmark_runs(limit=1000)) == 3


def test_sqlite_backup_and_restore_preserve_user_data(tmp_path):
    source = tmp_path / "live.sqlite3"
    backup = tmp_path / "backup.sqlite3"
    restored = tmp_path / "restored.sqlite3"
    db = Database("sqlite:///" + source.as_posix())
    user_id = db.ensure_user("backup@example.test", "Backup User")
    db.add_memory("preserve this memory", user_id=user_id)

    assert db.backup_to(backup) == backup
    Database.restore_backup_to(backup, restored)

    restored_db = Database("sqlite:///" + restored.as_posix())
    assert restored_db.list_memories(user_id=user_id) == ["preserve this memory"]
    with restored_db.Session() as session:
        assert session.query(User).filter_by(id=user_id).one().email == "backup@example.test"


def test_sqlite_backup_refuses_live_database_and_existing_destination(tmp_path):
    source = tmp_path / "live.sqlite3"
    db = Database("sqlite:///" + source.as_posix())
    db.init()

    with pytest.raises(ValueError, match="differ"):
        db.backup_to(source)

    existing = tmp_path / "existing.sqlite3"
    existing.write_bytes(b"keep existing file")
    with pytest.raises(FileExistsError):
        db.backup_to(existing)
    assert existing.read_bytes() == b"keep existing file"


def test_sqlite_restore_refuses_existing_destination(tmp_path):
    backup = tmp_path / "backup.sqlite3"
    destination = tmp_path / "destination.sqlite3"
    db = Database("sqlite:///" + backup.as_posix())
    db.init()
    db.backup_to(tmp_path / "valid-backup.sqlite3")
    valid_backup = tmp_path / "valid-backup.sqlite3"
    destination.write_bytes(b"do not overwrite")

    with pytest.raises(FileExistsError):
        Database.restore_backup_to(valid_backup, destination)
    assert destination.read_bytes() == b"do not overwrite"


def test_sqlite_restore_rejects_corrupt_backup_without_leaving_destination(tmp_path):
    corrupt = tmp_path / "corrupt.sqlite3"
    destination = tmp_path / "restored.sqlite3"
    corrupt.write_bytes(b"not a sqlite database")

    with pytest.raises(Exception):
        Database.restore_backup_to(corrupt, destination)
    assert not destination.exists()


def test_sqlite_restore_rejects_backup_missing_core_tables(tmp_path):
    import sqlite3

    incomplete = tmp_path / "incomplete.sqlite3"
    destination = tmp_path / "restored.sqlite3"
    with sqlite3.connect(incomplete) as connection:
        connection.execute("CREATE TABLE users (id INTEGER PRIMARY KEY)")
        connection.execute("CREATE TABLE memories (id INTEGER PRIMARY KEY)")

    with pytest.raises(ValueError, match="benchmark_runs.*conversations.*knowledge_fingerprints"):
        Database.restore_backup_to(incomplete, destination)
    assert not destination.exists()


def test_sqlite_backup_rejects_in_memory_database(tmp_path):
    db = Database("sqlite:///:memory:")
    with pytest.raises(ValueError, match="file-backed"):
        db.backup_to(tmp_path / "memory-backup.sqlite3")
    assert not (tmp_path / "memory-backup.sqlite3").exists()

def test_conversation_history_is_isolated_between_users(tmp_path):
    db = Database("sqlite:///" + (tmp_path / "tenant-history.sqlite3").as_posix())
    db.init()
    alice_id = db.ensure_user("alice@example.test", "Alice")
    bob_id = db.ensure_user("bob@example.test", "Bob")

    db.save_chat_pair(
        "Alice private question", "Alice private answer",
        conversation_id="alice-private-thread", user_id=alice_id,
    )

    assert db.load_history(
        conversation_id="alice-private-thread", user_id=alice_id
    )[0]["user"] == "Alice private question"
    assert db.load_history(
        conversation_id="alice-private-thread", user_id=bob_id
    ) == []
    assert db.list_conversations(user_id=bob_id) == []
    assert db.delete_conversation(
        "alice-private-thread", user_id=bob_id
    ) is False
    assert db.load_history(
        conversation_id="alice-private-thread", user_id=alice_id
    )[0]["assistant"] == "Alice private answer"


def test_user_cannot_reuse_another_users_conversation_id(tmp_path):
    db = Database("sqlite:///" + (tmp_path / "tenant-write.sqlite3").as_posix())
    db.init()
    alice_id = db.ensure_user("alice@example.test", "Alice")
    bob_id = db.ensure_user("bob@example.test", "Bob")

    db.save_chat_pair(
        "Original owner message", "Original owner answer",
        conversation_id="shared-thread-id", user_id=alice_id,
    )

    with pytest.raises(PermissionError, match="does not belong"):
        db.save_chat_pair(
            "Unauthorized overwrite attempt", "Should not be stored",
            conversation_id="shared-thread-id", user_id=bob_id,
        )

    history = db.load_history(
        conversation_id="shared-thread-id", user_id=alice_id
    )
    assert len(history) == 1
    assert history[0]["user"] == "Original owner message"

