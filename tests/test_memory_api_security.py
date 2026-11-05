"""Regression tests for authenticated personal memory endpoints."""

import asyncio

from tamanna_ai.authentication.access_control import TamannaAccessControl


async def _status_for(method: str, path: str) -> int:
    async def app(scope, receive, send):
        await send({"type": "http.response.start", "status": 200, "headers": []})
        await send({"type": "http.response.body", "body": b"ok"})

    middleware = TamannaAccessControl(app)
    scope = {
        "type": "http",
        "method": method,
        "path": path,
        "headers": [],
    }
    messages = []

    async def receive():
        return {"type": "http.request", "body": b"", "more_body": False}

    async def send(message):
        messages.append(message)

    await middleware(scope, receive, send)
    return next(item["status"] for item in messages if item["type"] == "http.response.start")


def test_memory_collection_read_requires_login():
    assert asyncio.run(_status_for("GET", "/api/memory")) == 401


def test_memory_creation_requires_login():
    assert asyncio.run(_status_for("POST", "/api/memory")) == 401


def test_memory_update_requires_login():
    assert asyncio.run(_status_for("PATCH", "/api/memory/123")) == 401


def test_memory_deletion_requires_login():
    assert asyncio.run(_status_for("DELETE", "/api/memory/123")) == 401
