"""Tamanna AI WAF event logger.
Writes security events as JSON Lines.
Sensitive dictionary fields are redacted before writing.
"""
import json
import os
from datetime import datetime, timezone
from threading import Lock
from typing import Any, Dict, Mapping
class WAFEventLogger:
    """Append WAF events to a local JSONL file."""
    SENSITIVE_KEYS = {
        "authorization",
        "cookie",
        "set-cookie",
        "password",
        "passwd",
        "token",
        "access_token",
        "refresh_token",
        "api_key",
        "secret",
    }
    def __init__(self, config: Mapping[str, Any]) -> None:
        self.config = dict(config)
        self.logging_config = dict(self.config.get("logging", {}))
        self.enabled = bool(self.logging_config.get("enabled", True))
        self.redact_secrets = bool(
            self.logging_config.get("redact_secrets", True)
        )
        self.max_event_size = int(
            self.logging_config.get("max_event_size_bytes", 16384)
        )
        self.file_path = str(
            self.logging_config.get(
                "file", "data/waf_events.jsonl"
            )
        )
        self._lock = Lock()
    def _redact(self, value: Any) -> Any:
        """Recursively redact values associated with sensitive keys."""
        if isinstance(value, dict):
            result = {}
            for key, item in value.items():
                if (
                    self.redact_secrets
                    and str(key).lower() in self.SENSITIVE_KEYS
                ):
                    result[key] = "[REDACTED]"
                else:
                    result[key] = self._redact(item)
            return result
        if isinstance(value, list):
            return [self._redact(item) for item in value]
        return value
    def log_event(self, event: Mapping[str, Any]) -> Dict[str, Any]:
        """Write one event and return its logging status."""
        if not self.enabled:
            return {"logged": False, "reason": "logging_disabled"}
        if not isinstance(event, Mapping):
            return {"logged": False, "reason": "invalid_event"}
        record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "project": "Tamanna AI",
            "component": "WAF",
            "event": self._redact(dict(event)),
        }
        try:
            encoded = json.dumps(
                record, ensure_ascii=False, separators=(",", ":")
            )
        except (TypeError, ValueError):
            return {"logged": False, "reason": "event_not_json_serializable"}
        if len(encoded.encode("utf-8")) > self.max_event_size:
            return {"logged": False, "reason": "event_too_large"}
        try:
            directory = os.path.dirname(self.file_path)
            if directory:
                os.makedirs(directory, exist_ok=True)
            with self._lock:
                with open(self.file_path, "a", encoding="utf-8") as handle:
                    handle.write(encoded + "\n")
            return {"logged": True, "file": self.file_path}
        except OSError:
            # Avoid returning event contents or sensitive filesystem details.
            return {"logged": False, "reason": "storage_error"}