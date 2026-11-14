"""Dependency-free local chat demo for the Tamanna AI runner.

This is a small rule-based demo, not the production Tamanna AI model.
It deliberately binds to loopback by default and does not call an external AI API.
"""
from __future__ import annotations

import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

MAX_REQUEST_BYTES = 16 * 1024


def ai_reply(message: str) -> str:
    """Return a deterministic local demo response."""
    text = message.strip()
    normalized = text.casefold()
    if not text:
        return "Please enter a message."
    if "hello" in normalized or normalized == "hi":
        return "Hi! How can I help you?"
    if "your name" in normalized or "who are you" in normalized or "name" in normalized:
        return "I am Tamanna AI, running in local demo mode."
    if "how are you" in normalized:
        return "I am running normally. How can I help?"
    return f"You said: {text}"


class ChatHandler(BaseHTTPRequestHandler):
    server_version = "TamannaLocalChat/1.0"

    def _send_json(self, status: int, payload: dict[str, Any]) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        if self.path == "/health":
            self._send_json(200, {"status": "ok", "mode": "local-demo"})
            return
        self._send_json(404, {"error": "not_found"})

    def do_POST(self) -> None:
        if self.path != "/chat":
            self._send_json(404, {"error": "not_found"})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            self._send_json(400, {"error": "invalid_content_length"})
            return
        if length <= 0:
            self._send_json(400, {"error": "empty_request"})
            return
        if length > MAX_REQUEST_BYTES:
            self._send_json(413, {"error": "request_too_large"})
            return
        try:
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            self._send_json(400, {"error": "invalid_json"})
            return
        if not isinstance(payload, dict) or not isinstance(payload.get("message"), str):
            self._send_json(400, {"error": "message_must_be_a_string"})
            return
        message = payload["message"].strip()
        if not message:
            self._send_json(400, {"error": "message_required"})
            return
        self._send_json(200, {"reply": ai_reply(message), "mode": "local-demo"})


def main() -> None:
    host = os.environ.get("TAMANNA_CHAT_HOST", "127.0.0.1")
    try:
        port = int(os.environ.get("TAMANNA_CHAT_PORT", "5000"))
    except ValueError as exc:
        raise SystemExit("TAMANNA_CHAT_PORT must be an integer") from exc
    if not 0 < port < 65536:
        raise SystemExit("TAMANNA_CHAT_PORT must be between 1 and 65535")
    with ThreadingHTTPServer((host, port), ChatHandler) as server:
        print(f"Tamanna local chat demo listening on http://{host}:{port}")
        server.serve_forever()


if __name__ == "__main__":
    main()
