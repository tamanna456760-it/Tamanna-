"""Regression tests for the protected admin control-center API."""
import sqlite3

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from tamanna_ai.admin_control_api import router
from tamanna_ai.authentication import router as auth


@pytest.fixture
def admin_client(monkeypatch, tmp_path):
    database = tmp_path / "admin-api.sqlite3"
    monkeypatch.setattr(auth, "DB", database)
    import tamanna_ai.admin_control_api as admin_api
    from tamanna_ai.persistence.database import Database
    app_database = Database("sqlite:///" + str(tmp_path / "application.sqlite3"))
    app_database.init()
    monkeypatch.setattr(admin_api, "database", app_database)
    monkeypatch.setattr(admin_api, "AUTH_DB", database)
    monkeypatch.setattr(admin_api, "current_user", lambda token: {
        "id": 1, "email": "admin@example.test", "name": "Admin"
    } if token == "valid-session" else None)
    monkeypatch.setenv("TAMANNA_ADMIN_EMAIL", "admin@example.test")
    monkeypatch.setenv("TAMANNA_SESSION_SECRET", "test-only-session-secret-with-at-least-32-characters")
    auth.init_db()
    with sqlite3.connect(database) as db:
        db.execute(
            "INSERT INTO users(email,name,password_hash,created_at,updated_at) VALUES(?,?,?,?,?)",
            ("admin@example.test", "Admin", "never-return-this-hash", "2026-01-01", "2026-01-01"),
        )
        db.execute(
            "INSERT INTO users(email,name,password_hash,created_at,updated_at) VALUES(?,?,?,?,?)",
            ("member@example.test", "Member", "another-secret-hash", "2026-01-02", "2026-01-02"),
        )
    app = FastAPI()
    app.include_router(router)
    return TestClient(app)


def test_admin_endpoints_reject_anonymous_requests(admin_client):
    assert admin_client.get("/api/admin/users").status_code == 401
    assert admin_client.get("/api/admin/analytics").status_code == 401


def test_user_listing_never_returns_password_hashes(admin_client):
    response = admin_client.get("/api/admin/users", cookies={auth.COOKIE: "valid-session"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] == 2
    assert payload["users"][0]["email"] == "member@example.test"
    assert all("password_hash" not in user for user in payload["users"])


def test_settings_are_allowlisted_and_audited(admin_client):
    cookies = {auth.COOKIE: "valid-session"}
    response = admin_client.patch(
        "/api/admin/settings",
        cookies=cookies,
        headers={"Origin": "https://www.bd-king-r7.com"},
        json={"values": {"maintenance_mode": True, "default_language": "bn"}},
    )
    assert response.status_code == 200
    settings = admin_client.get("/api/admin/settings", cookies=cookies)
    assert settings.status_code == 200
    assert settings.json()["settings"]["maintenance_mode"] is True
    assert settings.json()["settings"]["default_language"] == "bn"
    logs = admin_client.get("/api/admin/audit-logs", cookies=cookies)
    assert logs.status_code == 200
    assert logs.json()["total"] == 1
    rejected = admin_client.patch(
        "/api/admin/settings",
        cookies=cookies,
        headers={"Origin": "https://www.bd-king-r7.com"},
        json={"values": {"session_secret": "do-not-store"}},
    )
    assert rejected.status_code == 422


def test_analytics_and_deployment_are_truthful(admin_client):
    cookies = {auth.COOKIE: "valid-session"}
    analytics = admin_client.get("/api/admin/analytics", cookies=cookies)
    assert analytics.status_code == 200
    assert analytics.json()["analytics"]["registered_users"] == 2
    deployment = admin_client.get("/api/admin/deployment", cookies=cookies)
    assert deployment.status_code == 200
    assert deployment.json()["deployment"]["deployment_actions"] == "not_supported_by_this_endpoint"
