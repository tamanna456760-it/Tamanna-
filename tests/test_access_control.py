"""Regression tests for Tamanna privileged API middleware."""
import asyncio

import tamanna_ai.authentication.access_control as access


def invoke(middleware, path="/api/code-builder/propose", headers=None, method="POST"):
    messages = []
    scope = {
        "type": "http",
        "method": method,
        "path": path,
        "headers": headers or [],
    }

    async def receive():
        return {"type": "http.request", "body": b"", "more_body": False}

    async def send(message):
        messages.append(message)

    asyncio.run(middleware(scope, receive, send))
    return messages


def status(messages):
    return next(m["status"] for m in messages if m["type"] == "http.response.start")


def test_code_propose_requires_login(monkeypatch):
    monkeypatch.setattr(access, "current_user", lambda token: None)
    app = access.TamannaAccessControl(lambda *args: None)
    result = invoke(app, headers=[])
    assert status(result) == 401


def test_code_propose_requires_admin(monkeypatch):
    monkeypatch.setenv("TAMANNA_ADMIN_EMAIL", "admin@tamanna.com")
    monkeypatch.setattr(access, "current_user", lambda token: {"email": "user@tamanna.com"})
    app = access.TamannaAccessControl(lambda *args: None)
    result = invoke(app, headers=[(b"cookie", b"tamanna_session=test")])
    assert status(result) == 403


def test_code_propose_rejects_untrusted_origin(monkeypatch):
    monkeypatch.setenv("TAMANNA_ADMIN_EMAIL", "admin@tamanna.com")
    monkeypatch.setattr(access, "current_user", lambda token: {"email": "admin@tamanna.com"})
    app = access.TamannaAccessControl(lambda *args: None)
    result = invoke(app, headers=[
        (b"cookie", b"tamanna_session=test"),
        (b"origin", b"https://attacker.example"),
    ])
    assert status(result) == 403


def test_code_propose_allows_configured_admin(monkeypatch):
    monkeypatch.setenv("TAMANNA_ADMIN_EMAIL", "admin@tamanna.com")
    monkeypatch.setenv("TAMANNA_CORS_ORIGINS", "https://www.tamanna.com")
    monkeypatch.setattr(access, "current_user", lambda token: {"email": "admin@tamanna.com"})
    called = []

    async def downstream(scope, receive, send):
        called.append(True)
        await send({"type": "http.response.start", "status": 204, "headers": []})
        await send({"type": "http.response.body", "body": b""})

    app = access.TamannaAccessControl(downstream)
    result = invoke(app, headers=[
        (b"cookie", b"tamanna_session=test"),
        (b"origin", b"https://www.tamanna.com"),
    ])
    assert called == [True]
    assert status(result) == 204



def test_chat_and_planning_routes_require_login(monkeypatch):
    monkeypatch.setattr(access, "current_user", lambda token: None)
    app = access.TamannaAccessControl(lambda *args: None)

    protected_paths = [
        "/api/chat",
        "/api/chat/master",
        "/api/tamanna/echo",
        "/api/autonomous/plan",
        "/api/code-builder/plan",
    ]

    for path in protected_paths:
        result = invoke(app, path=path, headers=[])
        assert status(result) == 401, path


def test_project_inventory_and_status_gets_require_login(monkeypatch):
    monkeypatch.setattr(access, "current_user", lambda token: None)
    app = access.TamannaAccessControl(lambda *args: None)

    protected_paths = [
        "/api/autonomous/files",
        "/api/autonomous/think",
        "/api/autonomous/startup",
        "/api/linux/tools",
        "/api/linux/status",
        "/api/linux/shell/status",
        "/api/self-healing/status",
        "/api/code-builder/project",
        "/api/unified/project",
        "/api/security/tools",
    ]

    for path in protected_paths:
        result = invoke(app, path=path, headers=[], method="GET")
        assert status(result) == 401, path


def test_skill_matching_and_code_inspection_require_login(monkeypatch):
    monkeypatch.setattr(access, "current_user", lambda token: None)
    app = access.TamannaAccessControl(lambda *args: None)

    for path in ["/api/skills/match", "/api/code-builder/inspect"]:
        result = invoke(app, path=path, headers=[])
        assert status(result) == 401, path


def test_sensitive_status_endpoints_require_login(monkeypatch):
    monkeypatch.setattr(access, "current_user", lambda token: None)
    app = access.TamannaAccessControl(lambda *args: None)

    for path in ["/api/self-improvement/status", "/api/tamanna/system"]:
        result = invoke(app, path=path, headers=[], method="GET")
        assert status(result) == 401, path


def test_admin_signup_requires_bootstrap_token(monkeypatch):
    from fastapi import HTTPException
    from tamanna_ai.authentication.router import authorize_admin_signup

    monkeypatch.setenv("TAMANNA_ADMIN_EMAIL", "Tamanna456760@gmail.com")
    monkeypatch.delenv("TAMANNA_ADMIN_SIGNUP_TOKEN", raising=False)

    try:
        authorize_admin_signup("tamanna456760@gmail.com", None)
        assert False, "Admin signup must fail closed without a bootstrap token."
    except HTTPException as exc:
        assert exc.status_code == 503

    monkeypatch.setenv("TAMANNA_ADMIN_SIGNUP_TOKEN", "a" * 48)
    try:
        authorize_admin_signup("TAManna456760@gmail.com", "wrong-token")
        assert False, "Incorrect bootstrap token must be rejected."
    except HTTPException as exc:
        assert exc.status_code == 403

    authorize_admin_signup("tamanna456760@gmail.com", "a" * 48)


def test_regular_signup_does_not_need_admin_bootstrap_token(monkeypatch):
    from tamanna_ai.authentication.router import authorize_admin_signup

    monkeypatch.setenv("TAMANNA_ADMIN_EMAIL", "admin@tamanna.com")
    monkeypatch.delenv("TAMANNA_ADMIN_SIGNUP_TOKEN", raising=False)
    authorize_admin_signup("member@example.com", None)
