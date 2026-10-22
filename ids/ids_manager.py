File: ids/ids_manager.py

"""
Tamanna AI Intrusion Detection System Manager.
Coordinates event collection, intrusion detection, and alert management.
Default operation is monitor-only. No automatic blocking or firewall changes.
"""
from __future__ import annotations
from typing import Any
from ids.alert_manager import AlertManager
from ids.detection_engine import DetectionEngine
from ids.event_collector import EventCollector
class IDSManager:
    """Coordinate Tamanna AI IDS components in monitor-only mode."""
    def __init__(
        self,
        *,
        enabled: bool = True,
        mode: str = "monitor_only",
        max_events: int = 1000,
        max_event_size: int = 16384,
        max_alerts: int = 1000,
        minimum_severity: str = "medium",
        failed_login_threshold: int = 5,
        failed_login_window: int = 300,
        request_rate_threshold: int = 60,
        request_rate_window: int = 60,
    ) -> None:
        if mode != "monitor_only":
            raise ValueError(
                "Only monitor_only mode is supported."
            )
        self.enabled = bool(enabled)
        self.mode = mode
        self.collector = EventCollector(
            max_events=max_events,
            max_event_size=max_event_size,
        )
        self.detector = DetectionEngine(
            failed_login_threshold=failed_login_threshold,
            failed_login_window=failed_login_window,
            request_rate_threshold=request_rate_threshold,
            request_rate_window=request_rate_window,
        )
        self.alert_manager = AlertManager(
            max_alerts=max_alerts,
            minimum_severity=minimum_severity,
        )
    def _record_event(self, event: dict[str, Any]) -> bool:
        """Record an event without changing system security settings."""
        if not self.enabled:
            return False
        return self.collector.add_event(event)
    def _process_alert(self, alert: Any) -> Any:
        """Store a detection alert when one is generated."""
        if alert is None:
            return None
        if not isinstance(alert, dict):
            raise TypeError("Detection engine alert must be a dictionary.")
        safe_alert = dict(alert)
        safe_alert["action"] = "alert_only"
        safe_alert["system_firewall_modified"] = False
        self.alert_manager.add_alert(safe_alert)
        return safe_alert
    def record_event(self, event: dict[str, Any]) -> bool:
        """Collect a general security event."""
        if not isinstance(event, dict):
            raise TypeError("event must be a dictionary")
        return self._record_event(event)
    def record_failed_login(
        self,
        client_id: str,
        *,
        now: float | None = None,
    ) -> Any:
        """Record a failed login and process any resulting alert."""
        if not self.enabled:
            return None
        self._record_event({
            "type": "failed_login",
            "client_id": client_id,
        })
        alert = self.detector.record_failed_login(
            client_id,
            now=now,
        )
        return self._process_alert(alert)
    def record_request(
        self,
        client_id: str,
        path: str = "/",
        *,
        now: float | None = None,
    ) -> Any:
        """Record a request and process any resulting alert."""
        if not self.enabled:
            return None
        self._record_event({
            "type": "request",
            "client_id": client_id,
            "path": path,
        })
        alert = self.detector.record_request(
            client_id,
            path=path,
            now=now,
        )
        return self._process_alert(alert)
    def recent_events(self, limit: int = 100) -> list[dict[str, Any]]:
        """Return recent collected events."""
        return self.collector.recent(limit=limit)
    def recent_alerts(
        self,
        limit: int = 100,
        minimum_severity: str | None = None,
    ) -> list[dict[str, Any]]:
        """Return recent alerts."""
        return self.alert_manager.recent_alerts(
            limit=limit,
            minimum_severity=minimum_severity,
        )
    def summary(self) -> dict[str, Any]:
        """Return a compact IDS status summary."""
        return {
            "project": "Tamanna AI",
            "owner": "HM INSAN ALI",
            "enabled": self.enabled,
            "mode": self.mode,
            "event_count": self.collector.count(),
            "alert_count": self.alert_manager.count(),
            "automatic_ip_blocking": False,
            "system_firewall_modified": False,
        }
    def health(self) -> dict[str, Any]:
        """Return component health information."""
        return {
            "project": "Tamanna AI",
            "enabled": self.enabled,
            "mode": self.mode,
            "collector": self.collector.health(),
            "detector": self.detector.health(),
            "alerts": self.alert_manager.summary(),
            "system_firewall_modified": False,
        }