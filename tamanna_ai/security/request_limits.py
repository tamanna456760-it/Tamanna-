"""ASGI request-body size guard."""
from __future__ import annotations
import os
from starlette.responses import JSONResponse

class RequestSizeLimitMiddleware:
    def __init__(self, app, max_bytes: int | None = None):
        self.app = app
        self.max_bytes = max_bytes or int(os.getenv("TAMANNA_MAX_REQUEST_BYTES", "1048576"))
        if self.max_bytes < 1024:
            raise ValueError("TAMANNA_MAX_REQUEST_BYTES must be at least 1024")

    async def __call__(self, scope, receive, send):
        if scope.get("type") != "http":
            await self.app(scope, receive, send)
            return

        headers = dict(scope.get("headers", []))
        declared = headers.get(b"content-length")
        if declared:
            try:
                if int(declared) > self.max_bytes:
                    await JSONResponse(
                        {"detail": "Request body exceeds the configured size limit."},
                        status_code=413,
                    )(scope, receive, send)
                    return
            except ValueError:
                await JSONResponse(
                    {"detail": "Invalid Content-Length header."},
                    status_code=400,
                )(scope, receive, send)
                return

        chunks = []
        total = 0
        while True:
            message = await receive()
            if message["type"] == "http.disconnect":
                return
            if message["type"] != "http.request":
                continue
            body = message.get("body", b"")
            total += len(body)
            if total > self.max_bytes:
                await JSONResponse(
                    {"detail": "Request body exceeds the configured size limit."},
                    status_code=413,
                )(scope, receive, send)
                return
            chunks.append(body)
            if not message.get("more_body", False):
                break

        body = b"".join(chunks)
        consumed = False

        async def replay_receive():
            nonlocal consumed
            if not consumed:
                consumed = True
                return {"type": "http.request", "body": body, "more_body": False}
            return {"type": "http.disconnect"}

        await self.app(scope, replay_receive, send)


class SecurityHeadersMiddleware:
    """Add baseline browser security headers to every HTTP response."""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope.get("type") != "http":
            await self.app(scope, receive, send)
            return

        async def send_with_security_headers(message):
            if message["type"] == "http.response.start":
                headers = [
                    (name, value)
                    for name, value in message.get("headers", [])
                    if name.lower() not in {
                        b"x-content-type-options",
                        b"x-frame-options",
                        b"referrer-policy",
                        b"permissions-policy",
                        b"strict-transport-security",
                    }
                ]
                headers.extend([
                    (b"x-content-type-options", b"nosniff"),
                    (b"x-frame-options", b"DENY"),
                    (b"referrer-policy", b"strict-origin-when-cross-origin"),
                    (b"permissions-policy", b"camera=(), microphone=(), geolocation=()"),
                ])
                if scope.get("scheme") == "https":
                    headers.append((
                        b"strict-transport-security",
                        b"max-age=31536000; includeSubDomains",
                    ))
                message = {**message, "headers": headers}
            await send(message)

        await self.app(scope, receive, send_with_security_headers)
