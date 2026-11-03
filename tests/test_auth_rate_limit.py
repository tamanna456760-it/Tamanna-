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
