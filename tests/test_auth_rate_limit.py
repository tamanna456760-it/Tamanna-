from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from tamanna_ai.authentication import router as auth


def test_auth_rate_limit_persists_and_hashes_ip(tmp_path, monkeypatch):
    monkeypatch.setenv("TAMANNA_SESSION_SECRET", "test-only-session-secret-which-is-long-enough")
    monkeypatch.setattr(auth, "DB", tmp_path / "auth.sqlite3")
    auth.init_db()
    request = SimpleNamespace(client=SimpleNamespace(host="198.51.100.25"))

    for _ in range(10):
        auth.rate_limit_auth(request, "login")

    with pytest.raises(HTTPException) as exc:
        auth.rate_limit_auth(request, "login")

    assert exc.value.status_code == 429
    with auth.db() as connection:
        rows = connection.execute("SELECT ip_hash FROM auth_attempts").fetchall()
    assert len(rows) == 10
    assert all("198.51.100.25" not in row["ip_hash"] for row in rows)


def test_auth_rate_limit_separates_actions_and_ips(tmp_path, monkeypatch):
    monkeypatch.setenv("TAMANNA_SESSION_SECRET", "test-only-session-secret-which-is-long-enough")
    monkeypatch.setattr(auth, "DB", tmp_path / "auth.sqlite3")
    auth.init_db()
    first_ip = SimpleNamespace(client=SimpleNamespace(host="198.51.100.25"))
    second_ip = SimpleNamespace(client=SimpleNamespace(host="198.51.100.26"))

    for _ in range(10):
        auth.rate_limit_auth(first_ip, "login")

    auth.rate_limit_auth(first_ip, "signup")
    auth.rate_limit_auth(second_ip, "login")



def test_authenticated_action_rate_limit_is_per_account_and_persistent(tmp_path, monkeypatch):
    monkeypatch.setenv("TAMANNA_SESSION_SECRET", "test-only-session-secret-which-is-long-enough")
    monkeypatch.setattr(auth, "DB", tmp_path / "auth.sqlite3")
    auth.init_db()

    for _ in range(30):
        auth.rate_limit_user_action(42, "chat", limit=30, window_seconds=60)

    with pytest.raises(HTTPException) as exc:
        auth.rate_limit_user_action(42, "chat", limit=30, window_seconds=60)
    assert exc.value.status_code == 429

    # Another account has an independent quota.
    auth.rate_limit_user_action(43, "chat", limit=30, window_seconds=60)

    with auth.db() as connection:
        rows = connection.execute(
            "SELECT ip_hash, action FROM auth_attempts WHERE action='chat'"
        ).fetchall()
    assert len(rows) == 31
    assert all(len(row["ip_hash"]) == 64 for row in rows)
    assert all(
        all(character in "0123456789abcdef" for character in row["ip_hash"])
        for row in rows
    )
    assert all(str(42) not in row["ip_hash"] for row in rows)


def test_authenticated_action_rate_limit_expires_after_window(tmp_path, monkeypatch):
    monkeypatch.setenv("TAMANNA_SESSION_SECRET", "test-only-session-secret-which-is-long-enough")
    monkeypatch.setattr(auth, "DB", tmp_path / "auth.sqlite3")
    auth.init_db()
    clock = [1_800_000_000]
    monkeypatch.setattr(auth.time, "time", lambda: clock[0])

    auth.rate_limit_user_action(42, "chat", limit=2, window_seconds=60)
    auth.rate_limit_user_action(42, "chat", limit=2, window_seconds=60)
    with pytest.raises(HTTPException) as exc:
        auth.rate_limit_user_action(42, "chat", limit=2, window_seconds=60)
    assert exc.value.status_code == 429

    # At the exact 60-second boundary, the previous requests are outside the window.
    clock[0] += 60
    auth.rate_limit_user_action(42, "chat", limit=2, window_seconds=60)

    with auth.db() as connection:
        count = connection.execute(
            "SELECT COUNT(*) FROM auth_attempts WHERE action='chat' AND attempted_at>=?",
            (clock[0] - 60,),
        ).fetchone()[0]
    assert count == 1
