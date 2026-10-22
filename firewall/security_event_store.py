"""
Tamanna AI Firewall - Security Event Store
Owner: HM INSAN ALI
Stores security events in a local JSONL file.
This module does not block traffic or modify system firewall rules.
"""
import json
import os
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
DEFAULT_EVENT_PATH = (
    Path(__file__).resolve().parent
    / "data"
    / "security_events.jsonl"
)
ALLOWED_SEVERITIES = {"INFO", "LOW", "MEDIUM", "HIGH", "CRITICAL"}
MAX_EVENT_BYTES = 16_384
_SECRET_KEYS = {
    "authorization",
    "password",
    "passwd",
    "token",
    "access_token",
    "api_key",
    "secret",
    "private_key",
}
def _redact(value: Any, depth: int = 0) -> Any:
    """Redact common secret fields from nested event details."""
    if depth > 8:
        return "[MAX_DEPTH]"
    if isinstance(value, dict):
        cleaned = {}
        for key, item in value.items():
            normalized = str(key).lower().replace("-", "_")
            if (
                normalized in _SECRET_KEYS
                or normalized.endswith("_token")
                or normalized.endswith("_secret")
            ):
                cleaned[str(key)] = "[REDACTED]"
            else:
                cleaned[str(key)] = _redact(item, depth + 1)
        return cleaned
    if isinstance(value, (list, tuple)):
        return [_redact(item, depth + 1) for item in value[:100]]
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return str(value)[:1000]
class SecurityEventStore:
    """Thread-safe local JSONL security event writer."""
    def __init__(
        self,
        path: str | Path = DEFAULT_EVENT_PATH,
    ):
        self.path = Path(path)
        self._lock = threading.Lock()
    def append_event(
        self,
        event_type: str,
        severity: str = "INFO",
        details: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Validate and append one event; return the saved event."""
        if not isinstance(event_type, str) or not event_type.strip():
            raise ValueError("event_type must be a non-empty string")
        severity = str(severity).upper()
        if severity not in ALLOWED_SEVERITIES:
            raise ValueError("Unsupported event severity")
        if details is None:
            details = {}
        if not isinstance(details, dict):
            raise TypeError("details must be a dictionary")
        event = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event_type": event_type.strip()[:200],
            "severity": severity,
            "details": _redact(details),
        }
        encoded = json.dumps(
            event,
            ensure_ascii=False,
            separators=(",", ":"),
        )
        if len(encoded.encode("utf-8")) > MAX_EVENT_BYTES:
            raise ValueError("Security event exceeds maximum size")
        with self._lock:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            # O_APPEND keeps each writer positioned at the end.
            # The lock coordinates threads using this instance only.
            with self.path.open("a", encoding="utf-8") as file:
                file.write(encoded + "\n")
                file.flush()
                os.fsync(file.fileno())
        return event
    def read_events(self, limit: int = 100) -> list[dict[str, Any]]:
        """Read the most recent valid events without changing the log."""
        if not isinstance(limit, int) or isinstance(limit, bool):
            raise TypeError("limit must be an integer")
        if limit < 1 or limit > 10_000:
            raise ValueError("limit must be between 1 and 10000")
        if not self.path.is_file():
            return []
        with self._lock:
            with self.path.open("r", encoding="utf-8") as file:
                lines = file.readlines()
        events = []
        for line in lines[-limit:]:
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(event, dict):
                events.append(event)
        return events
if __name__ == "__main__":
    store = SecurityEventStore()
    saved = store.append_event(
        event_type="security_event_store_started",
        severity="INFO",
        details={"project": "Tamanna AI"},
    )
    print(json.dumps(saved, indent=2, ensure_ascii=False))