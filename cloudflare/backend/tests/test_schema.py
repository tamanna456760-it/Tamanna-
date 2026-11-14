"""Cloudflare D1 schema regression tests using Python's SQLite engine.

These tests need no Cloudflare credentials or network access. They verify that
the checked-in D1 SQL remains valid SQLite and creates the expected tables.
"""
from pathlib import Path
import sqlite3


BACKEND_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = BACKEND_ROOT / "schema.sql"


def test_d1_schema_exists_and_executes():
    assert SCHEMA_PATH.is_file(), "cloudflare/backend/schema.sql is missing"

    connection = sqlite3.connect(":memory:")
    try:
        connection.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
        tables = {
            row[0]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            )
        }
        expected = {
            "users",
            "sessions",
            "preferences",
            "messages",
            "auth_attempts",
            "chat_requests",
        }
        assert expected <= tables
    finally:
        connection.close()


def test_schema_enforces_message_role_constraint():
    connection = sqlite3.connect(":memory:")
    try:
        connection.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
        with connection:
            connection.execute(
                "INSERT INTO users (user_id, email, name, password_hash, created_at) "
                "VALUES ('u1', 'user@example.test', 'Test User', 'hash', '2026-01-01')"
            )
        try:
            connection.execute(
                "INSERT INTO messages (user_id, role, content, created_at) "
                "VALUES ('u1', 'system', 'not an allowed role', '2026-01-01')"
            )
        except sqlite3.IntegrityError:
            pass
        else:
            raise AssertionError("messages.role accepted an unsupported value")
    finally:
        connection.close()
