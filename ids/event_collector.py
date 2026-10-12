"""Security event collector for Tamanna AI IDS.
Owner: HM INSAN ALI
Monitor-only: no automatic blocking or firewall modifications.
"""
from __future__ import annotations
import json
import re
import time
from collections import deque
from datetime import datetime, timezone
from threading import Lock
from typing import Any
SECRET_KEY_PATTERN = re.compile(
    r"(password|passwd|token|secret|api[_-]?key|authorization|cookie)",
    re.IGNORECASE,
)
SUSPICIOUS_PATHS = (
    "/.env",
    "/.git",
    "/wp-admin",
    "/wp-login.php",
    "/etc/passwd",
    "/phpmyadmin",
)
class EventCollector:
    """Validate, redact, and retain a bounded number of security events."""
    def __init__(
        self,
        max_events: int = 1000,
        max_event_size: int = 16384,
    ) -> None:
        if isinstance(max_events, bool) or not isinstance(max_events, int):
            raise ValueError("max_events must be an integer")
        if isinstance(max_event_size, bool) or not isinstance(max_event_size, int):
            raise ValueError("max_event_size must be an integer")
        if max_events < 1:
            raise ValueError("max_events must be at least 1")
        if max_event_size < 128:
            raise ValueError("max_event_size must be at least 128 bytes")
        self.max_events = max_events
        self.max_event_size = max_event_size
        self._events: deque[dict[str, Any]] = deque(maxlen=max_events)
        self._lock = Lock()
    @staticmethod
    def _redact(value: Any) -> Any:
        """Redact secret-like dictionary keys recursively."""
        if isinstance(value, dict):
            cleaned = {}
            for key, item in value.items():
                safe_key = str(key)[:128]
                if SECRET_KEY_PATTERN.search(safe_key):
                    cleaned[safe_key] = "[REDACTED]"
                else:
                    cleaned[safe_key] = EventCollector._redact(item)
            return cleaned
        if isinstance(value, list):
            return [EventCollector._redact(item) for item in value[:100]]
        if isinstance(value, str):
            return value[:4096]
        if value is None or isinstance(value, (bool, int, float)):
            return value
        return "[UNSUPPORTED_VALUE]"
    def collect(self, event: dict[str, Any]) -> dict[str, Any]:
        """Collect one event or raise ValueError for invalid input."""
        if not isinstance(event, dict):
            raise ValueError("Event must be a JSON-style object")
        safe_event = self._redact(event)
        try:
            encoded = json.dumps(
                safe_event,
                ensure_ascii=False,
                allow_nan=False,
                separators=(",", ":"),
            ).encode("utf-8")
        except (TypeError, ValueError) as exc:
            raise ValueError("Event contains invalid data") from exc
        if len(encoded) > self.max_event_size:
            raise ValueError("Event exceeds the configured size limit")
        now = datetime.now(timezone.utc).isoformat()
        normalized = {
            "timestamp": now,
            "event": safe_event,
        }
        with self._lock:
            self._events.append(normalized)
        return {
            "accepted": True,
            "timestamp": now,
            "event_count": self.count(),
        }
    def count(self) -> int:
        """Return the current number of retained events."""
        with self._lock:
            return len(self._events)
    def recent(self, limit: int = 100) -> list[dict[str, Any]]:
        """Return a copy of the most recent retained events."""
        if isinstance(limit, bool) or not isinstance(limit, int) or limit < 1:
            raise ValueError("limit must be a positive integer")
        with self._lock:
            events = list(self._events)
        return events[-limit:]
    def inspect_path(self, path: str) -> list[str]:
        """Return detection indicators for a suspicious request path."""
        if not isinstance(path, str):
            return ["invalid_path_type"]
        normalized = path.strip().lower().split("?", 1)[0]
        indicators = []
        if "\x00" in normalized or "\\" in normalized:
            indicators.append("malformed_path")
        if any(marker in normalized for marker in SUSPICIOUS_PATHS):
            indicators.append("suspicious_path")
        if re.search(r"(^|/)\.\.(?:/|$)", normalized):
            indicators.append("path_traversal_pattern")
        return indicators
    def health(self) -> dict[str, Any]:
        """Return basic collector health information."""
        return {
            "project": "Tamanna AI",
            "component": "IDS Event Collector",
            "status": "OK",
            "mode": "monitor_only",
            "events_retained": self.count(),
            "max_events": self.max_events,
            "system_firewall_modified": False,
        }