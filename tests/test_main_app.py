"""End-to-end smoke tests for the primary FastAPI application."""

from fastapi.testclient import TestClient


def test_main_app_imports_and_health_endpoint(monkeypatch, tmp_path):
    monkeypatch.setenv(
        "TAMANNA_SESSION_SECRET",
        "test-only-session-secret-do-not-use-in-production-123456",
    )
    monkeypatch.setenv("TAMANNA_ADMIN_EMAIL", "admin@example.test")
    monkeypatch.setenv("TAMANNA_COOKIE_SECURE", "0")
    monkeypatch.setenv("TAMANNA_GEMINI_CHAT", "0")

    import tamanna_ai.authentication.router as auth_router

    monkeypatch.setattr(auth_router, "DB", tmp_path / "accounts.sqlite3")

    import Main

    with TestClient(Main.app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
