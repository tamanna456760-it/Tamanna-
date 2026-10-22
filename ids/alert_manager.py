"""Alert manager for Tamanna AI IDS.
Owner: HM INSAN ALI
Monitor-only: alerts are recorded for review; no automatic enforcement.
"""
from __future__ import annotations
from collections import deque
from datetime import datetime, timezone
from threading import Lock
from typing import Any
SEVERITY_LEVELS = {
    "low": 1,
    "medium": 2,
    "high": 3,
    "critical": 4,
}
class AlertManager:
    """Validate, normalize, and retain a bounded number of security alerts."""
    def __init__(
        self,
        max_alerts: int = 1000,
        minimum_severity: str = "medium",
    ) -> None:
        if (
            isinstance(max_alerts, bool)
            or not isinstance(max_alerts, int)
            or max_alerts < 1
        ):
            raise ValueError("max_alerts must be a positive integer")
        if minimum_severity not in SEVERITY_LEVELS:
            raise ValueError(
                "minimum_severity must be low, medium, high, or critical"
            )
        self.max_alerts = max_alerts
        self.minimum_severity = minimum_severity
        self._alerts: deque[dict[str, Any]] = deque(maxlen=max_alerts)
        self._lock = Lock()
    def add_alert(self, alert: dict[str, Any]) -> dict[str, Any]:
        """Record an alert if its severity meets the configured minimum."""
        if not isinstance(alert, dict):
            raise ValueError("alert must be a dictionary")
        severity = alert.get("severity")
        if not isinstance(severity, str):
            raise ValueError("alert severity is required")
        severity = severity.lower().strip()
        if severity not in SEVERITY_LEVELS:
            raise ValueError("unsupported alert severity")
        if SEVERITY_LEVELS[severity] < SEVERITY_LEVELS[self.minimum_severity]:
            return {
                "accepted": False,
                "reason": "below_minimum_severity",
                "alert_count": self.count(),
            }
        rule = alert.get("rule")
        reason = alert.get("reason")
        client_id = alert.get("client_id", "unknown")
        if not isinstance(rule, str) or not rule.strip():
            raise ValueError("alert rule must be a non-empty string")
        if not isinstance(reason, str) or not reason.strip():
            raise ValueError("alert reason must be a non-empty string")
        if not isinstance(client_id, str):
            raise ValueError("client_id must be a string")
        normalized = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "project": "Tamanna AI",
            "owner": "HM INSAN ALI",
            "rule": rule.strip()[:128],
            "severity": severity,
            "client_id": client_id.strip()[:128],
            "reason": reason.strip()[:1000],
            "action": "alert_only",
            "system_firewall_modified": False,
        }
        with self._lock:
            self._alerts.append(normalized)
            total = len(self._alerts)
        return {
            "accepted": True,
            "alert": normalized.copy(),
            "alert_count": total,
        }
    def count(self) -> int:
        """Return the number of alerts currently retained."""
        with self._lock:
            return len(self._alerts)
    def recent_alerts(
        self,
        limit: int = 100,
        minimum_severity: str | None = None,
    ) -> list[dict[str, Any]]:
        """Return recent alerts, optionally filtered by severity."""
        if isinstance(limit, bool) or not isinstance(limit, int) or limit < 1:
            raise ValueError("limit must be a positive integer")
        if (
            minimum_severity is not None
            and minimum_severity not in SEVERITY_LEVELS
        ):
            raise ValueError("unsupported minimum_severity")
        with self._lock:
            alerts = list(self._alerts)
        if minimum_severity is not None:
            minimum = SEVERITY_LEVELS[minimum_severity]
            alerts = [
                item for item in alerts
                if SEVERITY_LEVELS[item["severity"]] >= minimum
            ]
        return [item.copy() for item in alerts[-limit:]]
    def summary(self) -> dict[str, Any]:
        """Summarize retained alerts by severity."""
        with self._lock:
            alerts = list(self._alerts)
        counts = {severity: 0 for severity in SEVERITY_LEVELS}
        for alert in alerts:
            counts[alert["severity"]] += 1
        return {
            "project": "Tamanna AI",
            "component": "IDS Alert Manager",
            "total_alerts": len(alerts),
            "by_severity": counts,
            "minimum_severity": self.minimum_severity,
            "mode": "monitor_only",
            "system_firewall_modified": False,
        }