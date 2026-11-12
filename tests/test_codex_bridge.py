"""Security and configuration tests for the optional Codex bridge."""
from fastapi import FastAPI
from fastapi.testclient import TestClient

from tamanna_ai.integrations import codex_bridge as bridge
from tamanna_ai.authentication import router as auth


def make_client(monkeypatch, admin=True):
    monkeypatch.setattr(
        bridge, "current_user",
        lambda token: ({"id": 7, "email": "admin@example.test"} if admin and token == "valid" else None),
    )
    monkeypatch.setattr(bridge, "rate_limit_user_action", lambda *args, **kwargs: None)
    monkeypatch.setattr(bridge, "check_origin", lambda request: None)
    monkeypatch.setenv("TAMANNA_ADMIN_EMAIL", "admin@example.test")
    app = FastAPI()
    app.include_router(bridge.router)
    return TestClient(app)


def test_codex_status_requires_admin(monkeypatch):
    client = make_client(monkeypatch, admin=False)
    response = client.get("/api/codex/status", cookies={auth.COOKIE: "invalid"})
    assert response.status_code == 401


def test_codex_status_reports_disabled_without_exposing_secrets(monkeypatch):
    client = make_client(monkeypatch)
    monkeypatch.delenv("TAMANNA_CODEX_ENABLED", raising=False)
    response = client.get("/api/codex/status", cookies={auth.COOKIE: "valid"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["enabled"] is False
    assert payload["default_sandbox"] == "read-only"
    assert "token" not in payload


def test_codex_task_is_disabled_by_default(monkeypatch):
    client = make_client(monkeypatch)
    monkeypatch.delenv("TAMANNA_CODEX_ENABLED", raising=False)
    response = client.post(
        "/api/codex/tasks",
        cookies={auth.COOKIE: "valid"},
        json={"prompt": "Inspect the API route structure"},
    )
    assert response.status_code == 503
