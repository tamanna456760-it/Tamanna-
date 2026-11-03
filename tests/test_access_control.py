"""Regression tests for sensitive-route access control."""

from fastapi import FastAPI
from fastapi.testclient import TestClient

from tamanna_ai.authentication.access_control import TamannaAccessControl


def test_tamanna_echo_requires_login(monkeypatch):
    app = FastAPI()
    app.add_middleware(TamannaAccessControl)

    @app.post("/api/tamanna/echo")
    def echo():
        return {"ok": True}

    monkeypatch.delenv("TAMANNA_ADMIN_EMAIL", raising=False)
    response = TestClient(app).post("/api/tamanna/echo", json={"message": "status"})

    assert response.status_code == 401
    assert response.json()["detail"] == "Sign in required."


def test_chat_route_requires_login():
    app = FastAPI()
    app.add_middleware(TamannaAccessControl)

    @app.post("/api/chat")
    def chat():
        return {"ok": True}

    response = TestClient(app).post("/api/chat", json={"message": "hello"})

    assert response.status_code == 401
    assert response.json()["detail"] == "Sign in required."
