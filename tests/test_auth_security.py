"""Security regression tests for auth, protected routes, CORS and body limits."""
import time
from types import SimpleNamespace

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from starlette.requests import Request

from tamanna_ai.authentication import router as auth
from tamanna_ai.authentication import access_control
from tamanna_ai.security.request_limits import (
    RequestSizeLimitMiddleware,
    SecurityHeadersMiddleware,
)


def _request_with_origin(origin: str) -> Request:
    return Request({
        "type": "http",
        "http_version": "1.1",
        "method": "POST",
        "scheme": "https",
        "path": "/api/auth/login",
        "raw_path": b"/api/auth/login",
        "query_string": b"",
        "headers": [(b"origin", origin.encode("latin-1"))],
        "client": ("127.0.0.1", 1234),
        "server": ("testserver", 443),
    })


def test_password_hashing_is_salted_and_verifiable():
    stored = auth.password_hash("correct horse battery")
    assert stored != "correct horse battery"
    assert auth.password_ok("correct horse battery", stored)
    assert not auth.password_ok("wrong password", stored)
    parts = stored.split("$")
    weak = "$".join([parts[0], "100", parts[2], parts[3]])
    assert not auth.password_ok("correct horse battery", weak)


def test_expired_signed_token_is_rejected(monkeypatch):
    monkeypatch.setenv("TAMANNA_SESSION_SECRET", "test-session-secret-with-more-than-32-characters")
    payload = f"1.{int(time.time()) - 1}.expirednonce"
    token = payload + "." + auth.sign(payload)
    assert auth.current_user(token) is None


def test_origin_allowlist_is_exact(monkeypatch):
    monkeypatch.setenv("TAMANNA_CORS_ORIGINS", "https://www.bd-king-r7.com")
    auth.check_origin(_request_with_origin("https://www.bd-king-r7.com"))
    with pytest.raises(Exception) as exc:
        auth.check_origin(_request_with_origin("https://www.bd-king-r7.com.evil.test"))
    assert getattr(exc.value, "status_code", None) == 403


def test_request_body_limit_returns_413():
    app = FastAPI()
    app.add_middleware(RequestSizeLimitMiddleware, max_bytes=1024)

    @app.post("/echo")
    async def echo(payload: dict):
        return payload

    response = TestClient(app).post("/echo", content=b"x" * 2048,
                                    headers={"content-type": "application/json"})
    assert response.status_code == 413


def test_every_user_protected_route_rejects_anonymous_write():
    app = FastAPI()
    app.add_middleware(access_control.TamannaAccessControl)
    client = TestClient(app)
    blocked = access_control.BLOCKED_EXECUTION_ROUTES
    for path in sorted(access_control.USER_ROUTES):
        response = client.post(path, json={})
        expected = 410 if path in blocked else 401
        assert response.status_code == expected, (path, response.status_code)



def test_internal_read_routes_reject_anonymous_access():
    app = FastAPI()
    app.add_middleware(access_control.TamannaAccessControl)
    client = TestClient(app)

    for path in sorted(access_control.READ_ROUTES):
        response = client.get(path)
        assert response.status_code == 401, (path, response.status_code)


def test_admin_read_routes_reject_regular_authenticated_user(monkeypatch):
    app = FastAPI()
    app.add_middleware(access_control.TamannaAccessControl)
    monkeypatch.setattr(access_control, "current_user", lambda token: {
        "email": "regular@example.com", "id": 7,
    })
    monkeypatch.setenv("TAMANNA_ADMIN_EMAIL", "admin@example.com")

    @app.get("/api/admin/overview")
    async def admin_overview():
        return {"ok": True}

    response = TestClient(app).get(
        "/api/admin/overview",
        cookies={auth.COOKIE: "test-session"},
    )
    assert response.status_code == 403


def test_admin_read_routes_allow_configured_admin(monkeypatch):
    app = FastAPI()
    app.add_middleware(access_control.TamannaAccessControl)
    monkeypatch.setattr(access_control, "current_user", lambda token: {
        "email": "admin@example.com", "id": 8,
    })
    monkeypatch.setenv("TAMANNA_ADMIN_EMAIL", "admin@example.com")

    @app.get("/api/admin/overview")
    async def admin_overview():
        return {"ok": True}

    response = TestClient(app).get(
        "/api/admin/overview",
        cookies={auth.COOKIE: "test-session"},
    )
    assert response.status_code == 200
    assert response.json() == {"ok": True}


def test_command_execution_routes_are_disabled_even_for_admin(monkeypatch):
    app = FastAPI()
    app.add_middleware(access_control.TamannaAccessControl)
    monkeypatch.setattr(access_control, "current_user", lambda token: {
        "email": "admin@example.com", "id": 1,
    })
    monkeypatch.setenv("TAMANNA_ADMIN_EMAIL", "admin@example.com")
    client = TestClient(app)
    for path in access_control.BLOCKED_EXECUTION_ROUTES:
        assert client.post(path, json={}).status_code == 410



def test_admin_only_routes_reject_regular_authenticated_user(monkeypatch):
    app = FastAPI()
    app.add_middleware(access_control.TamannaAccessControl)
    monkeypatch.setattr(access_control, "current_user", lambda token: {
        "email": "regular@example.com", "id": 2,
    })
    monkeypatch.setenv("TAMANNA_ADMIN_EMAIL", "admin@example.com")
    client = TestClient(app)
    for path in sorted(access_control.ADMIN_ROUTES - access_control.BLOCKED_EXECUTION_ROUTES):
        response = client.post(path, json={})
        assert response.status_code == 403, (path, response.status_code)




def test_admin_allowlist_supports_multiple_configured_emails(monkeypatch):
    app = FastAPI()
    app.add_middleware(access_control.TamannaAccessControl)
    monkeypatch.setattr(access_control, "current_user", lambda token: {
        "email": "second-admin@example.com", "id": 3,
    })
    monkeypatch.setenv(
        "TAMANNA_ADMIN_EMAIL",
        "first-admin@example.com, second-admin@example.com",
    )

    @app.post("/api/skills/create")
    async def create_skill():
        return {"ok": True}

    response = TestClient(app).post(
        "/api/skills/create",
        cookies={auth.COOKIE: "test-session"},
    )
    assert response.status_code == 200
    assert response.json() == {"ok": True}


def test_admin_allowlist_rejects_email_not_in_configured_list(monkeypatch):
    app = FastAPI()
    app.add_middleware(access_control.TamannaAccessControl)
    monkeypatch.setattr(access_control, "current_user", lambda token: {
        "email": "outsider@example.com", "id": 4,
    })
    monkeypatch.setenv(
        "TAMANNA_ADMIN_EMAIL",
        "first-admin@example.com, second-admin@example.com",
    )
    response = TestClient(app).post(
        "/api/skills/create",
        cookies={auth.COOKIE: "test-session"},
    )
    assert response.status_code == 403


def test_auth_rate_limit_fails_with_clear_503_when_session_secret_missing(monkeypatch, tmp_path):
    monkeypatch.delenv("TAMANNA_SESSION_SECRET", raising=False)
    monkeypatch.setattr(auth, "DB", tmp_path / "auth.sqlite3")
    request = SimpleNamespace(client=SimpleNamespace(host="198.51.100.44"))
    with pytest.raises(Exception) as exc:
        auth.rate_limit_auth(request, "login")
    assert getattr(exc.value, "status_code", None) == 503



def test_cors_allows_only_exact_configured_origin(monkeypatch):
    from Main import app
    client = TestClient(app)
    allowed = client.options(
        "/api/chat",
        headers={
            "Origin": "https://www.bd-king-r7.com",
            "Access-Control-Request-Method": "POST",
        },
    )
    assert allowed.status_code == 200
    assert allowed.headers.get("access-control-allow-origin") == "https://www.bd-king-r7.com"

    denied = client.options(
        "/api/chat",
        headers={
            "Origin": "https://www.bd-king-r7.com.attacker.invalid",
            "Access-Control-Request-Method": "POST",
        },
    )
    assert denied.status_code == 400
    assert "access-control-allow-origin" not in denied.headers

def test_unknown_login_email_performs_dummy_pbkdf2_verification(monkeypatch, tmp_path):
    from fastapi import Response
    from tamanna_ai.authentication.router import Login, login
    from unittest.mock import patch

    monkeypatch.setattr(auth, "DB", tmp_path / "dummy-login.sqlite3")
    auth.init_db()
    monkeypatch.setenv("TAMANNA_SESSION_SECRET", "test-session-secret-with-more-than-32-characters")
    request = SimpleNamespace(client=SimpleNamespace(host="198.51.100.25"), headers={})
    with patch.object(auth, "password_ok", wraps=auth.password_ok) as verify:
        with pytest.raises(Exception) as exc:
            login(Login(email="unknown@example.test", password="wrong-password"),
                  request=request, response=Response())
    assert getattr(exc.value, "status_code", None) == 401
    verify.assert_called_once()
    assert verify.call_args.args[1] == auth._DUMMY_PASSWORD_HASH


def test_unknown_and_wrong_password_login_errors_are_indistinguishable(monkeypatch, tmp_path):
    from fastapi import Response
    from tamanna_ai.authentication.router import Login, Signup, login, signup

    monkeypatch.setattr(auth, "DB", tmp_path / "generic-login.sqlite3")
    auth.init_db()
    monkeypatch.setenv("TAMANNA_SESSION_SECRET", "test-session-secret-with-more-than-32-characters")
    request = SimpleNamespace(client=SimpleNamespace(host="198.51.100.26"), headers={})
    signup(Signup(email="member@example.test", name="Member",
                  password="correct horse battery"), request=request, response=Response())
    failures = []
    for email in ("missing@example.test", "member@example.test"):
        with pytest.raises(Exception) as exc:
            login(Login(email=email, password="wrong-password"), request=request, response=Response())
        failures.append(exc.value)
    assert [getattr(error, "status_code", None) for error in failures] == [401, 401]
    assert [str(error.detail) for error in failures] == [str(failures[0].detail)] * 2


def test_auth_rate_limit_blocks_eleventh_attempt_and_is_action_scoped(monkeypatch, tmp_path):
    monkeypatch.setenv("TAMANNA_SESSION_SECRET", "test-session-secret-with-more-than-32-characters")
    monkeypatch.setattr(auth, "DB", tmp_path / "rate-limit.sqlite3")
    auth.init_db()
    request = SimpleNamespace(client=SimpleNamespace(host="198.51.100.80"))

    for _ in range(10):
        auth.rate_limit_auth(request, "login")
    with pytest.raises(Exception) as exc:
        auth.rate_limit_auth(request, "login")
    assert getattr(exc.value, "status_code", None) == 429

    # Signup has its own action bucket and must not inherit login failures.
    auth.rate_limit_auth(request, "signup")



def test_user_action_rate_limit_is_account_and_action_scoped(monkeypatch, tmp_path):
    monkeypatch.setenv(
        "TAMANNA_SESSION_SECRET",
        "test-only-session-secret-do-not-use-in-production-123456",
    )
    monkeypatch.setattr(auth, "DB", tmp_path / "user-action-rate-limit.sqlite3")
    auth.init_db()

    # Two accounts use the same action independently.
    auth.rate_limit_user_action(user_id=101, action="knowledge_import", limit=2)
    auth.rate_limit_user_action(user_id=101, action="knowledge_import", limit=2)
    with pytest.raises(Exception) as exc:
        auth.rate_limit_user_action(
            user_id=101, action="knowledge_import", limit=2
        )
    assert getattr(exc.value, "status_code", None) == 429

    # Another account and another action have independent buckets.
    auth.rate_limit_user_action(user_id=202, action="knowledge_import", limit=2)
    auth.rate_limit_user_action(user_id=101, action="knowledge_reindex", limit=1)


def test_user_action_rate_limit_fails_closed_without_session_secret(monkeypatch, tmp_path):
    monkeypatch.delenv("TAMANNA_SESSION_SECRET", raising=False)
    monkeypatch.setattr(auth, "DB", tmp_path / "user-action-no-secret.sqlite3")
    auth.init_db()

    with pytest.raises(Exception) as exc:
        auth.rate_limit_user_action(user_id=7, action="knowledge_import")
    assert getattr(exc.value, "status_code", None) == 503


def _create_auth_test_user(monkeypatch, tmp_path, filename="sessions.sqlite3"):
    monkeypatch.setenv("TAMANNA_SESSION_SECRET", "test-session-secret-with-more-than-32-characters")
    monkeypatch.setattr(auth, "DB", tmp_path / filename)
    auth.init_db()
    with auth.db() as conn:
        cursor = conn.execute(
            "INSERT INTO users(email,name,password_hash,created_at,updated_at) VALUES(?,?,?,?,?)",
            ("session-user@example.test", "Session User",
             auth.password_hash("correct horse battery"), auth.now(), auth.now()),
        )
        user_id = cursor.lastrowid
        conn.execute(
            "INSERT INTO preferences(user_id,data,updated_at) VALUES(?,?,?)",
            (user_id, "{}", auth.now()),
        )
    return user_id


def test_logout_revokes_server_side_session_and_clears_cookie(monkeypatch, tmp_path):
    from fastapi import Response

    user_id = _create_auth_test_user(monkeypatch, tmp_path, "logout.sqlite3")
    token = auth.issue_session(user_id)
    assert auth.current_user(token)["id"] == user_id

    response = Response()
    result = auth.logout(
        request=SimpleNamespace(headers={}),
        response=response,
        token=token,
    )

    assert result == {"ok": True}
    assert auth.current_user(token) is None
    assert "tamanna_session" in response.headers.get("set-cookie", "")


def test_password_change_revokes_all_existing_sessions(monkeypatch, tmp_path):
    from fastapi import Response
    from tamanna_ai.authentication.router import ChangePassword, change_password

    user_id = _create_auth_test_user(monkeypatch, tmp_path, "password-change.sqlite3")
    first_token = auth.issue_session(user_id)
    second_token = auth.issue_session(user_id)
    assert auth.current_user(first_token)
    assert auth.current_user(second_token)

    result = change_password(
        ChangePassword(
            current_password="correct horse battery",
            new_password="a much stronger replacement password",
        ),
        request=SimpleNamespace(headers={}),
        token=first_token,
    )

    assert result["ok"] is True
    assert auth.current_user(first_token) is None
    assert auth.current_user(second_token) is None
    with auth.db() as conn:
        stored = conn.execute(
            "SELECT password_hash FROM users WHERE id=?", (user_id,)
        ).fetchone()["password_hash"]
    assert auth.password_ok("a much stronger replacement password", stored)
    assert not auth.password_ok("correct horse battery", stored)



def test_profile_and_preferences_are_isolated_between_accounts(monkeypatch, tmp_path):
    from fastapi import FastAPI

    monkeypatch.setenv(
        "TAMANNA_SESSION_SECRET",
        "test-only-session-secret-do-not-use-in-production-123456",
    )
    monkeypatch.setattr(auth, "DB", tmp_path / "account-isolation.sqlite3")
    auth.init_db()
    user_a = _create_auth_test_user(monkeypatch, tmp_path, "account-isolation.sqlite3")
    with auth.db() as connection:
        cursor = connection.execute(
            "INSERT INTO users(email,name,password_hash,created_at,updated_at) VALUES(?,?,?,?,?)",
            ("second@example.test", "Second User",
             auth.password_hash("another correct password"), auth.now(), auth.now()),
        )
        user_b = cursor.lastrowid
        connection.execute(
            "INSERT INTO preferences(user_id,data,updated_at) VALUES(?,?,?)",
            (user_b, "{}", auth.now()),
        )

    app = FastAPI()
    app.include_router(auth.router)
    token_a = auth.issue_session(user_a)
    token_b = auth.issue_session(user_b)
    client_a = TestClient(app)
    client_b = TestClient(app)
    client_a.cookies.set(auth.COOKIE, token_a)
    client_b.cookies.set(auth.COOKIE, token_b)

    response = client_a.patch("/api/auth/profile", json={"name": "Updated A"})
    assert response.status_code == 200
    response = client_a.put(
        "/api/auth/preferences",
        json={"preferences": {"theme": "dark", "language": "bn"}},
    )
    assert response.status_code == 200

    assert client_a.get("/api/auth/me").json()["user"]["name"] == "Updated A"
    assert client_b.get("/api/auth/me").json()["user"]["name"] == "Second User"
    assert client_a.get("/api/auth/preferences").json()["preferences"] == {
        "theme": "dark", "language": "bn"
    }
    assert client_b.get("/api/auth/preferences").json()["preferences"] == {}


def test_password_change_revokes_only_the_current_accounts_sessions(monkeypatch, tmp_path):
    from fastapi import FastAPI

    monkeypatch.setenv(
        "TAMANNA_SESSION_SECRET",
        "test-only-session-secret-do-not-use-in-production-123456",
    )
    user_a = _create_auth_test_user(monkeypatch, tmp_path, "password-isolation.sqlite3")
    with auth.db() as connection:
        cursor = connection.execute(
            "INSERT INTO users(email,name,password_hash,created_at,updated_at) VALUES(?,?,?,?,?)",
            ("other@example.test", "Other User",
             auth.password_hash("another correct password"), auth.now(), auth.now()),
        )
        user_b = cursor.lastrowid
        connection.execute(
            "INSERT INTO preferences(user_id,data,updated_at) VALUES(?,?,?)",
            (user_b, "{}", auth.now()),
        )
    app = FastAPI()
    app.include_router(auth.router)
    token_a1, token_a2 = auth.issue_session(user_a), auth.issue_session(user_a)
    token_b = auth.issue_session(user_b)
    client_a = TestClient(app)
    client_b = TestClient(app)
    client_a.cookies.set(auth.COOKIE, token_a1)
    client_b.cookies.set(auth.COOKIE, token_b)

    response = client_a.post(
        "/api/auth/change-password",
        json={
            "current_password": "correct horse battery",
            "new_password": "a much stronger replacement password",
        },
    )
    assert response.status_code == 200
    assert auth.current_user(token_a1) is None
    assert auth.current_user(token_a2) is None
    assert auth.current_user(token_b)["id"] == user_b
    assert client_b.get("/api/auth/me").status_code == 200


def test_auth_schema_initialization_is_idempotent_and_preserves_accounts(monkeypatch, tmp_path):
    user_id = _create_auth_test_user(monkeypatch, tmp_path, "schema-idempotent.sqlite3")
    token = auth.issue_session(user_id)

    auth.init_db()
    auth.init_db()

    assert auth.current_user(token)["id"] == user_id
    with auth.db() as conn:
        assert conn.execute("PRAGMA foreign_key_check").fetchall() == []
        assert conn.execute(
            "SELECT COUNT(*) FROM preferences WHERE user_id=?", (user_id,)
        ).fetchone()[0] == 1


def test_auth_user_foreign_keys_cascade_preferences_and_sessions(monkeypatch, tmp_path):
    user_id = _create_auth_test_user(monkeypatch, tmp_path, "schema-cascade.sqlite3")
    auth.issue_session(user_id)

    with auth.db() as conn:
        assert conn.execute("PRAGMA foreign_keys").fetchone()[0] == 1
        conn.execute("DELETE FROM users WHERE id=?", (user_id,))
        assert conn.execute(
            "SELECT COUNT(*) FROM preferences WHERE user_id=?", (user_id,)
        ).fetchone()[0] == 0
        assert conn.execute(
            "SELECT COUNT(*) FROM sessions WHERE user_id=?", (user_id,)
        ).fetchone()[0] == 0
        assert conn.execute("PRAGMA foreign_key_check").fetchall() == []


def test_model_admin_controls_fail_closed_without_configured_admin(monkeypatch):
    from tamanna_ai.api import routes as api_routes

    monkeypatch.delenv("TAMANNA_ADMIN_EMAIL", raising=False)
    monkeypatch.setattr(api_routes, "require_user", lambda token: {
        "email": "tamanna456760@gmail.com", "id": 1,
    })
    with pytest.raises(Exception) as exc:
        api_routes._require_model_admin("session")
    assert getattr(exc.value, "status_code", None) == 503


def test_model_admin_controls_support_configured_admin_allowlist(monkeypatch):
    from tamanna_ai.api import routes as api_routes

    monkeypatch.setenv(
        "TAMANNA_ADMIN_EMAIL",
        "first-admin@example.test, second-admin@example.test",
    )
    monkeypatch.setattr(api_routes, "require_user", lambda token: {
        "email": " SECOND-ADMIN@example.test ", "id": 2,
    })
    assert api_routes._require_model_admin("session")["id"] == 2

    monkeypatch.setattr(api_routes, "require_user", lambda token: {
        "email": "outsider@example.test", "id": 3,
    })
    with pytest.raises(Exception) as exc:
        api_routes._require_model_admin("session")
    assert getattr(exc.value, "status_code", None) == 403


def test_profile_cannot_change_email_and_wrong_password_preserves_sessions(monkeypatch, tmp_path):
    from fastapi import FastAPI

    user_id = _create_auth_test_user(monkeypatch, tmp_path, "profile-password-guards.sqlite3")
    app = FastAPI()
    app.include_router(auth.router)
    token = auth.issue_session(user_id)
    client = TestClient(app)
    client.cookies.set(auth.COOKIE, token)

    profile = client.patch(
        "/api/auth/profile",
        json={"name": "Safe Name", "email": "attacker@example.test"},
    )
    assert profile.status_code == 200
    assert client.get("/api/auth/me").json()["user"]["email"] == "session-user@example.test"
    assert client.get("/api/auth/me").json()["user"]["name"] == "Safe Name"

    failed = client.post(
        "/api/auth/change-password",
        json={
            "current_password": "not-the-current-password",
            "new_password": "a much stronger replacement password",
        },
    )
    assert failed.status_code == 400
    assert auth.current_user(token)["id"] == user_id
    with auth.db() as connection:
        stored = connection.execute(
            "SELECT password_hash FROM users WHERE id=?", (user_id,)
        ).fetchone()["password_hash"]
    assert auth.password_ok("correct horse battery", stored)


def test_session_cookie_has_http_only_secure_and_samesite_policy(monkeypatch):
    from fastapi import Response

    monkeypatch.setattr(auth, "COOKIE_SECURE", True)
    response = Response()
    auth.set_cookie(response, "test-session-token")
    cookie = response.headers.get("set-cookie", "").lower()

    assert "httponly" in cookie
    assert "secure" in cookie
    assert "samesite=lax" in cookie
    assert "path=/" in cookie
    assert f"max-age={auth.LIFETIME}" in cookie



def test_expired_or_revoked_session_cannot_access_account_endpoints(monkeypatch, tmp_path):
    from fastapi import FastAPI

    user_id = _create_auth_test_user(monkeypatch, tmp_path, "session-endpoints.sqlite3")
    app = FastAPI()
    app.include_router(auth.router)
    client = TestClient(app)

    valid_token = auth.issue_session(user_id)
    client.cookies.set(auth.COOKIE, valid_token)
    assert client.get("/api/auth/me").status_code == 200
    assert client.get("/api/auth/preferences").status_code == 200

    with auth.db() as connection:
        connection.execute(
            "DELETE FROM sessions WHERE token_hash=?",
            (__import__("hashlib").sha256(valid_token.encode()).hexdigest(),),
        )

    assert client.get("/api/auth/me").status_code == 401
    assert client.get("/api/auth/preferences").status_code == 401

    expired_payload = f"{user_id}.{int(time.time()) - 1}.expired-endpoint-nonce"
    expired_token = expired_payload + "." + auth.sign(expired_payload)
    client.cookies.set(auth.COOKIE, expired_token)
    assert client.get("/api/auth/me").status_code == 401
    assert client.get("/api/auth/preferences").status_code == 401

def test_expired_database_session_is_rejected_even_with_valid_signature(monkeypatch, tmp_path):
    monkeypatch.setenv(
        "TAMANNA_SESSION_SECRET",
        "test-only-session-secret-do-not-use-in-production-123456",
    )
    monkeypatch.setattr(auth, "DB", tmp_path / "expired-session.sqlite3")
    user_id = _create_auth_test_user(monkeypatch, tmp_path, "expired-session.sqlite3")

    payload = f"{user_id}.{int(time.time()) - 1}.expired-session-nonce"
    token = payload + "." + auth.sign(payload)
    token_hash = __import__("hashlib").sha256(token.encode()).hexdigest()
    with auth.db() as connection:
        connection.execute(
            "INSERT INTO sessions(token_hash,user_id,expires,created_at) VALUES(?,?,?,?)",
            (token_hash, user_id, int(time.time()) - 1, auth.now()),
        )

    assert auth.current_user(token) is None

def test_cross_site_origin_cannot_mutate_profile_or_revoke_session(monkeypatch, tmp_path):
    from fastapi import FastAPI

    user_id = _create_auth_test_user(monkeypatch, tmp_path, "csrf-origin.sqlite3")
    app = FastAPI()
    app.include_router(auth.router)
    token = auth.issue_session(user_id)
    client = TestClient(app)
    client.cookies.set(auth.COOKIE, token)

    denied_profile = client.patch(
        "/api/auth/profile",
        json={"name": "Cross-site Change"},
        headers={"Origin": "https://attacker.invalid"},
    )
    assert denied_profile.status_code == 403
    assert client.get("/api/auth/me").json()["user"]["name"] == "Session User"

    denied_logout = client.post(
        "/api/auth/logout",
        headers={"Origin": "https://attacker.invalid"},
    )
    assert denied_logout.status_code == 403
    assert auth.current_user(token)["id"] == user_id


def test_missing_origin_is_accepted_for_non_browser_client_compatibility(monkeypatch):
    # Native clients and server-to-server callers may omit Origin; browser
    # cross-site requests still carry an untrusted Origin and are rejected.
    request = SimpleNamespace(headers={})
    assert auth.check_origin(request) is None

def test_auth_database_enables_wal_foreign_keys_and_busy_timeout(monkeypatch, tmp_path):
    monkeypatch.setattr(auth, "DB", tmp_path / "database-pragmas.sqlite3")
    auth.init_db()

    with auth.db() as connection:
        assert connection.execute("PRAGMA foreign_keys").fetchone()[0] == 1
        assert connection.execute("PRAGMA journal_mode").fetchone()[0].lower() == "wal"
        assert connection.execute("PRAGMA busy_timeout").fetchone()[0] >= 10000


def test_session_cleanup_removes_expired_rows_when_issuing_new_session(monkeypatch, tmp_path):
    monkeypatch.setenv(
        "TAMANNA_SESSION_SECRET",
        "test-only-session-secret-do-not-use-in-production-123456",
    )
    monkeypatch.setattr(auth, "DB", tmp_path / "session-cleanup.sqlite3")
    user_id = _create_auth_test_user(monkeypatch, tmp_path, "session-cleanup.sqlite3")
    with auth.db() as connection:
        connection.execute(
            "INSERT INTO sessions(token_hash,user_id,expires,created_at) VALUES(?,?,?,?)",
            ("expired-placeholder-hash", user_id, int(time.time()) - 5, auth.now()),
        )

    token = auth.issue_session(user_id)
    assert auth.current_user(token)["id"] == user_id
    with auth.db() as connection:
        assert connection.execute(
            "SELECT COUNT(*) FROM sessions WHERE token_hash=?",
            ("expired-placeholder-hash",),
        ).fetchone()[0] == 0

def test_signup_duplicate_email_is_case_insensitive_and_does_not_create_second_account(monkeypatch, tmp_path):
    from fastapi import Response
    from tamanna_ai.authentication.router import Signup, signup

    monkeypatch.setenv(
        "TAMANNA_SESSION_SECRET",
        "test-only-session-secret-do-not-use-in-production-123456",
    )
    monkeypatch.setattr(auth, "DB", tmp_path / "duplicate-signup.sqlite3")
    auth.init_db()

    def request():
        return SimpleNamespace(
            client=SimpleNamespace(host="198.51.100.91"),
            headers={},
        )

    created = signup(
        Signup(email="Member@Example.Test", name="Member", password="correct horse battery"),
        request=request(),
        response=Response(),
    )
    assert created["user"]["email"] == "member@example.test"

    with pytest.raises(Exception) as exc:
        signup(
            Signup(email="member@example.test", name="Another", password="another correct password"),
            request=request(),
            response=Response(),
        )
    assert getattr(exc.value, "status_code", None) == 409
    with auth.db() as connection:
        assert connection.execute(
            "SELECT COUNT(*) FROM users WHERE email=? COLLATE NOCASE",
            ("member@example.test",),
        ).fetchone()[0] == 1

def test_concurrent_duplicate_signup_creates_exactly_one_account(monkeypatch, tmp_path):
    from concurrent.futures import ThreadPoolExecutor
    from fastapi import Response
    from tamanna_ai.authentication.router import Signup, signup

    monkeypatch.setenv(
        "TAMANNA_SESSION_SECRET",
        "test-only-session-secret-do-not-use-in-production-123456",
    )
    monkeypatch.setattr(auth, "DB", tmp_path / "concurrent-signup.sqlite3")
    auth.init_db()

    def attempt(name):
        request = SimpleNamespace(
            client=SimpleNamespace(host="198.51.100.92"),
            headers={},
        )
        try:
            signup(
                Signup(
                    email="race@example.test",
                    name=name,
                    password="correct horse battery",
                ),
                request=request,
                response=Response(),
            )
            return "created"
        except Exception as exc:
            return getattr(exc, "status_code", None)

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(attempt, ("First", "Second")))

    assert results.count("created") == 1
    assert results.count(409) == 1
    with auth.db() as connection:
        assert connection.execute(
            "SELECT COUNT(*) FROM users WHERE email=? COLLATE NOCASE",
            ("race@example.test",),
        ).fetchone()[0] == 1

def test_concurrent_auth_attempts_never_exceed_rate_limit(monkeypatch, tmp_path):
    from concurrent.futures import ThreadPoolExecutor

    monkeypatch.setenv(
        "TAMANNA_SESSION_SECRET",
        "test-only-session-secret-do-not-use-in-production-123456",
    )
    monkeypatch.setattr(auth, "DB", tmp_path / "concurrent-rate-limit.sqlite3")
    auth.init_db()
    request = SimpleNamespace(client=SimpleNamespace(host="198.51.100.93"))

    def attempt(_):
        try:
            auth.rate_limit_auth(request, "login")
            return "allowed"
        except Exception as exc:
            return getattr(exc, "status_code", None)

    with ThreadPoolExecutor(max_workers=16) as pool:
        results = list(pool.map(attempt, range(16)))

    assert results.count("allowed") == 10
    assert results.count(429) == 6
    with auth.db() as connection:
        stored = connection.execute(
            "SELECT COUNT(*) FROM auth_attempts WHERE action=?",
            ("login",),
        ).fetchone()[0]
    assert stored == 10

def test_session_cookie_has_secure_browser_attributes(monkeypatch):
    from fastapi import Response

    monkeypatch.setattr(auth, "COOKIE_SECURE", True)
    response = Response()
    auth.set_cookie(response, "test-session-token")

    cookie = response.headers.get("set-cookie", "").lower()
    assert "httponly" in cookie
    assert "secure" in cookie
    assert "samesite=lax" in cookie
    assert "path=/" in cookie

def test_cross_site_fetch_metadata_is_rejected_even_without_origin():
    request = SimpleNamespace(headers={"sec-fetch-site": "cross-site"})
    with pytest.raises(Exception) as exc:
        auth.check_origin(request)
    assert getattr(exc.value, "status_code", None) == 403


def test_same_origin_fetch_metadata_is_allowed_without_origin():
    request = SimpleNamespace(headers={"sec-fetch-site": "same-origin"})
    assert auth.check_origin(request) is None


def test_signup_rejects_whitespace_only_name_without_creating_account(monkeypatch, tmp_path):
    from fastapi import Response
    from tamanna_ai.authentication.router import Signup, signup

    monkeypatch.setenv(
        "TAMANNA_SESSION_SECRET",
        "test-only-session-secret-do-not-use-in-production-123456",
    )
    monkeypatch.setattr(auth, "DB", tmp_path / "blank-signup-name.sqlite3")
    auth.init_db()
    request = SimpleNamespace(
        client=SimpleNamespace(host="198.51.100.94"),
        headers={},
    )

    with pytest.raises(Exception) as exc:
        signup(
            Signup(
                email="blank-name@example.test",
                name="   ",
                password="correct horse battery",
            ),
            request=request,
            response=Response(),
        )

    assert getattr(exc.value, "status_code", None) == 422
    with auth.db() as connection:
        assert connection.execute(
            "SELECT COUNT(*) FROM users WHERE email=?",
            ("blank-name@example.test",),
        ).fetchone()[0] == 0


def test_same_site_fetch_metadata_without_origin_is_rejected():
    request = SimpleNamespace(headers={"sec-fetch-site": "same-site"})
    with pytest.raises(Exception) as exc:
        auth.check_origin(request)
    assert getattr(exc.value, "status_code", None) == 403


def test_same_site_fetch_metadata_with_allowlisted_origin_is_allowed(monkeypatch):
    monkeypatch.setenv("TAMANNA_CORS_ORIGINS", "https://www.bd-king-r7.com")
    request = SimpleNamespace(headers={
        "sec-fetch-site": "same-site",
        "origin": "https://www.bd-king-r7.com",
    })
    assert auth.check_origin(request) is None


def test_every_admin_read_route_rejects_regular_authenticated_user(monkeypatch):
    app = FastAPI()
    app.add_middleware(access_control.TamannaAccessControl)
    monkeypatch.setattr(access_control, "current_user", lambda token: {
        "email": "member@example.test", "id": 99,
    })
    monkeypatch.setenv("TAMANNA_ADMIN_EMAIL", "admin@example.test")
    client = TestClient(app)

    for path in sorted(access_control.ADMIN_READ_ROUTES):
        async def endpoint():
            return {"ok": True}

        app.add_api_route(path, endpoint, methods=["GET"])
        response = client.get(
            path,
            cookies={auth.COOKIE: "test-session"},
        )
        assert response.status_code == 403, (path, response.status_code)


def test_every_admin_read_route_fails_closed_without_admin_configuration(monkeypatch):
    app = FastAPI()
    app.add_middleware(access_control.TamannaAccessControl)
    monkeypatch.setattr(access_control, "current_user", lambda token: {
        "email": "admin@example.test", "id": 100,
    })
    monkeypatch.delenv("TAMANNA_ADMIN_EMAIL", raising=False)
    client = TestClient(app)

    for path in sorted(access_control.ADMIN_READ_ROUTES):
        async def endpoint():
            return {"ok": True}

        app.add_api_route(path, endpoint, methods=["GET"])
        response = client.get(
            path,
            cookies={auth.COOKIE: "test-session"},
        )
        assert response.status_code == 503, (path, response.status_code)


def test_security_headers_are_present_and_hsts_is_https_only():
    app = FastAPI()
    app.add_middleware(SecurityHeadersMiddleware)

    @app.get("/headers")
    async def headers():
        return {"ok": True}

    https_client = TestClient(app, base_url="https://testserver")
    https_response = https_client.get("/headers")
    assert https_response.headers["x-content-type-options"] == "nosniff"
    assert https_response.headers["x-frame-options"] == "DENY"
    assert https_response.headers["referrer-policy"] == "strict-origin-when-cross-origin"
    assert https_response.headers["permissions-policy"] == (
        "camera=(), microphone=(), geolocation=()"
    )
    assert https_response.headers["strict-transport-security"] == (
        "max-age=31536000; includeSubDomains"
    )

    http_client = TestClient(app, base_url="http://testserver")
    http_response = http_client.get("/headers")
    assert "strict-transport-security" not in http_response.headers
    assert http_response.headers["x-content-type-options"] == "nosniff"
