"""Small authenticated worker adapter for the Tamanna Central Server bridge.

The application supplies a handler that turns an instruction into a reply.
This module deliberately does not execute shell commands or modify repositories.
"""
import json
import os
import urllib.error
import urllib.request

class BridgeWorkerError(RuntimeError):
    pass

class TamannaBridgeWorker:
    def __init__(self, handler, base_url=None, service_token=None, timeout=20):
        self.base_url = (base_url or os.getenv("TAMANNA_BRIDGE_URL", "")).rstrip("/")
        self.service_token = service_token or os.getenv("TAMANNA_BRIDGE_SERVICE_TOKEN", "")
        self.handler = handler
        self.timeout = timeout
        if not self.base_url.startswith("https://") and not self.base_url.startswith("http://127.0.0.1"):
            raise BridgeWorkerError("Bridge URL must use HTTPS (HTTP only on localhost)")
        if len(self.service_token) < 32:
            raise BridgeWorkerError("TAMANNA_BRIDGE_SERVICE_TOKEN must be at least 32 characters")

    def _request(self, path, payload=None):
        body = None if payload is None else json.dumps(payload, ensure_ascii=False).encode("utf-8")
        req = urllib.request.Request(self.base_url + path, data=body, method="GET" if body is None else "POST", headers={
            "Authorization": "Bearer " + self.service_token,
            "Accept": "application/json",
            **({"Content-Type": "application/json"} if body is not None else {}),
        })
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                return json.loads(response.read().decode("utf-8"))
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as exc:
            raise BridgeWorkerError("Bridge request failed") from exc

    def process_one(self):
        message = self._request("/bridge/v1/consume", {})
        if message.get("status") == "empty":
            return {"status": "empty"}
        message_id = message.get("message_id")
        text = message.get("text")
        if not isinstance(message_id, str) or not isinstance(text, str):
            raise BridgeWorkerError("Bridge returned an invalid message")
        try:
            reply = self.handler(text, message.get("conversation_id", ""))
            if not isinstance(reply, str) or not reply.strip():
                raise BridgeWorkerError("Handler returned an empty response")
            result = self._request("/bridge/v1/reply", {"message_id": message_id, "reply": reply})
            return {"message_id": message_id, "status": result.get("status", "unknown")}
        except Exception:
            # Message remains processing for audit; automatic retry is intentionally not implicit.
            raise
