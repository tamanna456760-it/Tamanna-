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
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["service"] == "Tamanna AI"
    assert payload["storage"] == "sqlite"


def test_safe_tool_execution_requires_authenticated_session(monkeypatch, tmp_path):
    monkeypatch.setenv(
        "TAMANNA_SESSION_SECRET",
        "test-only-session-secret-do-not-use-in-production-123456",
    )
    monkeypatch.setenv("TAMANNA_ADMIN_EMAIL", "admin@example.test")
    monkeypatch.setenv("TAMANNA_COOKIE_SECURE", "0")
    monkeypatch.setenv("TAMANNA_CORS_ORIGINS", "http://testserver")

    import tamanna_ai.authentication.router as auth_router

    monkeypatch.setattr(auth_router, "DB", tmp_path / "tool-auth.sqlite3")
    import Main

    with TestClient(Main.app, base_url="https://testserver") as client:
        payload = {"name": "not-allow-listed", "arguments": {}}
        unauthenticated = client.post("/api/tools/execute", json=payload)
        assert unauthenticated.status_code == 401

        signup = client.post(
            "/api/auth/signup",
            json={
                "email": "member@example.test",
                "name": "Test Member",
                "password": "Strong-test-password-123!",
            },
        )
        assert signup.status_code == 201
        # Signup deliberately authenticates the new account; clear its cookie
        # to test the anonymous boundary independently.
        client.cookies.delete(auth_router.COOKIE)

        still_anonymous = client.post("/api/tools/execute", json=payload)
        assert still_anonymous.status_code == 401

        login = client.post(
            "/api/auth/login",
            json={
                "email": "member@example.test",
                "password": "Strong-test-password-123!",
            },
        )
        assert login.status_code == 200

        authenticated = client.post("/api/tools/execute", json=payload)
        assert authenticated.status_code == 422


def test_skills_and_code_builder_routes_reject_anonymous_access(monkeypatch, tmp_path):
    monkeypatch.setenv(
        "TAMANNA_SESSION_SECRET",
        "test-only-session-secret-do-not-use-in-production-123456",
    )
    monkeypatch.setenv("TAMANNA_ADMIN_EMAIL", "admin@example.test")
    monkeypatch.setenv("TAMANNA_COOKIE_SECURE", "0")

    import tamanna_ai.authentication.router as auth_router

    monkeypatch.setattr(auth_router, "DB", tmp_path / "feature-access.sqlite3")
    import Main

    with TestClient(Main.app) as client:
        assert client.get("/api/skills").status_code == 401
        assert client.get("/api/code-builder/status").status_code == 401
        assert client.get("/api/code-builder/scan").status_code == 401

def test_legacy_code_builder_and_unified_routes_are_not_public(monkeypatch, tmp_path):
    monkeypatch.setenv(
        "TAMANNA_SESSION_SECRET",
        "test-only-session-secret-do-not-use-in-production-123456",
    )
    monkeypatch.setenv("TAMANNA_ADMIN_EMAIL", "admin@example.test")
    monkeypatch.setenv("TAMANNA_COOKIE_SECURE", "0")

    import tamanna_ai.authentication.router as auth_router

    monkeypatch.setattr(auth_router, "DB", tmp_path / "legacy-builder-auth.sqlite3")
    import Main

    with TestClient(Main.app) as client:
        # Read/planning endpoints are private even when a duplicate legacy
        # code-builder implementation is registered later in Main.py.
        assert client.get("/api/code-builder/project").status_code == 401
        assert client.post(
            "/api/code-builder/plan", json={"request": "inspect project"}
        ).status_code == 401
        assert client.get("/api/unified/status").status_code == 401
        assert client.get("/api/unified/project").status_code == 401

        # Execution endpoints remain deliberately disabled, not merely hidden.
        assert client.post(
            "/api/code-builder/build", json={"files": []}
        ).status_code == 410
        assert client.post("/api/code-builder/compile").status_code == 410

def test_linux_and_command_routes_fail_closed_for_anonymous_users(monkeypatch, tmp_path):
    monkeypatch.setenv(
        "TAMANNA_SESSION_SECRET",
        "test-only-session-secret-do-not-use-in-production-123456",
    )
    monkeypatch.setenv("TAMANNA_ADMIN_EMAIL", "admin@example.test")
    monkeypatch.setenv("TAMANNA_COOKIE_SECURE", "0")

    import tamanna_ai.authentication.router as auth_router

    monkeypatch.setattr(auth_router, "DB", tmp_path / "linux-auth.sqlite3")
    import Main

    with TestClient(Main.app) as client:
        for path in (
            "/api/linux/tools",
            "/api/linux/status",
            "/api/linux/shell/status",
        ):
            assert client.get(path).status_code == 401

        for path, payload in (
            ("/api/linux/run", {"command": "id"}),
            ("/api/linux/shell", {"command": "id"}),
            ("/api/command", {"command": "id"}),
        ):
            response = client.post(path, json=payload)
            assert response.status_code == 410

        assert client.post(
            "/api/tamanna/echo", json={"message": "hello"}
        ).status_code == 401
