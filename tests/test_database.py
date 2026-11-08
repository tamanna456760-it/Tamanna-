"""Tests for SQLAlchemy chat persistence and safe legacy migration."""
import json
import pytest
from pathlib import Path
from sqlalchemy import inspect

from tamanna_ai.persistence.database import Database, Memory, User


def test_database_creates_required_tables_and_saves_chat(tmp_path):
    db = Database("sqlite:///" + (tmp_path / "chat.sqlite3").as_posix())
    db.init()
    db.save_chat_pair("hello", "hi there")
    history = db.load_history()
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
    assert db.load_history("legacy-import")[0]["user"] == "old question"
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
    memory_id = db.add_memory("keep this", metadata={"source": "test"})
    assert memory_id > 0
    assert db.list_memories() == ["keep this"]



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
