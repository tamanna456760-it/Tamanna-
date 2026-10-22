"""Security event logger for Tamanna AI Endpoint Security.
Owner: HM INSAN ALI
Writes structured JSON Lines events. This module does not modify
system settings or perform enforcement actions.
"""
from __future__ import annotations
import json
import os
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
class EndpointEventLogger:
    """Append bounded, redacted security events to a JSONL file."""
    SECRET_KEYS = {
        "password",
        "passwd",
        "token",
        "access_token",
        "refresh_token",
        "api_key",
        "authorization",
        "cookie",
        "secret",
    }
    def __init__(self, config: dict[str, Any]):
        self.config = config or {}
        self.settings = self.config.get("logging", {})
        self.enabled = self.settings.get("enabled", True)
        self.redact_secrets = self.settings.get("redact_secrets", True)
        self.max_event_size = int(
            self.settings.get("max_event_size_bytes", 16384)
        )
        if self.max_event_size < 256:
            raise ValueError("max_event_size_bytes must be at least 256")
        self.path = Path(
            self.settings.get(
                "file", "data/endpoint_security_events.jsonl"
            )
        )
        self._lock = threading.Lock()
    @classmethod
    def _redact(cls, value: Any) -> Any:
        """Redact values whose dictionary keys resemble secret names."""
        if isinstance(value, dict):
            cleaned = {}
            for key, item in value.items():
                key_text = str(key)
                normalized_key = key_text.lower().replace("-", "_")
                if normalized_key in cls.SECRET_KEYS:
                    cleaned[key_text] = "[REDACTED]"
                else:
                    cleaned[key_text] = cls._redact(item)
            return cleaned
        if isinstance(value, list):
            return [cls._redact(item) for item in value]
        return value
    def log_event(self, event: dict[str, Any]) -> dict[str, Any]:
        """Append one event; return a status instead of raising I/O errors."""
        if not self.enabled:
            return {"status": "disabled"}
        if not isinstance(event, dict):
            return {
                "status": "error",
                "reason": "event must be a dictionary",
            }
        record = dict(event)
        record.setdefault(
            "timestamp",
            datetime.now(timezone.utc).isoformat(),
        )
        record.setdefault("project", "Tamanna AI")
        record.setdefault("component", "Endpoint Security")
        if self.redact_secrets:
            record = self._redact(record)
        try:
            line = json.dumps(
                record,
                ensure_ascii=False,
                separators=(",", ":"),
            )
            if len(line.encode("utf-8")) > self.max_event_size:
                return {
                    "status": "error",
                    "reason": "event exceeds configured size limit",
                }
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with self._lock:
                with self.path.open("a", encoding="utf-8") as file_handle:
                    file_handle.write(line + "\n")
                    file_handle.flush()
                    os.fsync(file_handle.fileno())
            return {"status": "logged"}
        except (OSError, TypeError, ValueError) as exc:
            return {
                "status": "error",
                "reason": str(exc),
            }