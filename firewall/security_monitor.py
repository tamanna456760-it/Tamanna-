
"""
Tamanna AI — Advanced Security Monitor
Owner: HM INSAN ALI

Collects security events, evaluates severity, and creates reports.
Monitoring only: does not block IPs or modify operating-system rules.
"""

from __future__ import annotations

import json
import threading
from collections import Counter, deque
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


BASE_DIR = Path(__file__).resolve().parent
REPORT_DIR = BASE_DIR / "reports"

MAX_EVENTS = 10000
MAX_EVENT_LENGTH = 120
MAX_MESSAGE_LENGTH = 1000

VALID_SEVERITIES = {"info", "low", "medium", "high", "critical"}

# Do not include passwords, tokens, cookies, or request bodies in events.
SENSITIVE_KEYS = {
    "password",
    "passwd",
    "token",
    "access_token",
    "api_key",
    "secret",
    "authorization",
    "cookie",
    "private_key",
    "request_body",
}


def _sanitize(value: Any, depth: int = 0) -> Any:
    """Remove common secret fields and bound event size."""
    if depth > 5:
        return "[MAX_DEPTH]"

    if isinstance(value, dict):
        safe = {}

        for key, item in list(value.items())[:50]:
            name = str(key)[:100]

            if name.lower() in SENSITIVE_KEYS:
                safe[name] = "[REDACTED]"
            else:
                safe[name] = _sanitize(item, depth + 1)

        return safe

    if isinstance(value, (list, tuple)):
        return [_sanitize(item, depth + 1) for item in value[:50]]

    if isinstance(value, str):
        return value[:MAX_MESSAGE_LENGTH]

    if value is None or isinstance(value, (bool, int, float)):
        return value

    return f"[UNSUPPORTED:{type(value).__name__}]"


class SecurityMonitor:
    """Thread-safe in-memory event collector."""

    def __init__(self, max_events: int = MAX_EVENTS) -> None:
        if type(max_events) is not int or max_events < 1:
            raise ValueError("max_events must be a positive integer.")

        self._events: deque[dict[str, Any]] = deque(
            maxlen=max_events
        )
        self._lock = threading.Lock()

    def record(
        self,
        event: str,
        severity: str = "info",
        details: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Record a sanitized event in memory."""
        if not isinstance(event, str) or not event.strip():
            raise ValueError("Event name must not be empty.")

        if severity not in VALID_SEVERITIES:
            raise ValueError("Unsupported severity.")

        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event": event.strip()[:MAX_EVENT_LENGTH],
            "severity": severity,
            "details": _sanitize(
                details if isinstance(details, dict) else {}
            ),
        }

        with self._lock:
            self._events.append(entry)

        return entry.copy()

    def snapshot(self) -> list[dict[str, Any]]:
        """Return a copy of collected events."""
        with self._lock:
            return [event.copy() for event in self._events]

    def summary(self) -> dict[str, Any]:
        """Return counts by severity and event name."""
        events = self.snapshot()

        severity_counts = Counter(
            item["severity"] for item in events
        )
        event_counts = Counter(
            item["event"] for item in events
        )

        return {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "total_events": len(events),
            "by_severity": dict(severity_counts),
            "by_event": dict(event_counts),
            "automatic_blocking_enabled": False,
        }

    def export_report(self, output_file: str | Path | None = None) -> Path:
        """Write a JSON report for later review."""
        REPORT_DIR.mkdir(parents=True, exist_ok=True)

        destination = (
            Path(output_file)
            if output_file is not None
            else REPORT_DIR / "security_report.json"
        )

        report = {
            "summary": self.summary(),
            "events": self.snapshot(),
        }

        # Reports contain security metadata; protect the destination
        # directory and file permissions in production.
        destination.parent.mkdir(parents=True, exist_ok=True)
        with destination.open("w", encoding="utf-8") as file:
            json.dump(
                report,
                file,
                ensure_ascii=False,
                indent=2,
            )
            file.write("\n")

        return destination


_DEFAULT_MONITOR = SecurityMonitor()


def record_security_event(
    event: str,
    severity: str = "info",
    details: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Convenience function for other Tamanna security modules."""
    return _DEFAULT_MONITOR.record(event, severity, details)


if __name__ == "__main__":
    monitor = SecurityMonitor()

    monitor.record(
        "firewall_health_check",
        "info",
        {"mode": "audit_only"},
    )
    monitor.record(
        "repeated_failed_logins",
        "high",
        {"source": "test", "attempts": 5},
    )

    print(json.dumps(monitor.summary(), indent=2))
    print("Report saved to:", monitor.export_report())
