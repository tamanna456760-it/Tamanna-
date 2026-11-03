"""Security regression tests for auth, protected routes, CORS and body limits."""
import time
from types import SimpleNamespace

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from starlette.requests import Request

from tamanna_ai.authentication import router as auth
from tamanna_ai.authentication import access_control
from tamanna_ai.security.request_limits import RequestSizeLimitMiddleware


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
    monkeypatch.setenv("TAMANNA_CORS_ORIGINS", "https://www.tamanna.com,https://tamanna.com")
    auth.check_origin(_request_with_origin("https://www.tamanna.com"))
    with pytest.raises(Exception) as exc:
        auth.check_origin(_request_with_origin("https://www.tamanna.com.evil.test"))
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



def test_auth_rate_limit_fails_with_clear_503_when_session_secret_missing(monkeypatch, tmp_path):
    monkeypatch.delenv("TAMANNA_SESSION_SECRET", raising=False)
    monkeypatch.setattr(auth, "DB", tmp_path / "auth.sqlite3")
    request = SimpleNamespace(client=SimpleNamespace(host="198.51.100.44"))
    with pytest.raises(Exception) as exc:
        auth.rate_limit_auth(request, "login")
    assert getattr(exc.value, "status_code", None) == 503
