"""Detection engine for Tamanna AI IDS.
Owner: HM INSAN ALI
Monitor-only: detections generate alerts, never automatic blocks.
"""
from __future__ import annotations
import time
from collections import defaultdict, deque
from threading import Lock
from typing import Any
class DetectionEngine:
    """Detect repeated failures, high request rates, and suspicious paths."""
    def __init__(
        self,
        failed_login_threshold: int = 5,
        failed_login_window_seconds: int = 300,
        request_rate_threshold: int = 60,
        request_rate_window_seconds: int = 60,
    ) -> None:
        positive_settings = {
            "failed_login_threshold": failed_login_threshold,
            "failed_login_window_seconds": failed_login_window_seconds,
            "request_rate_threshold": request_rate_threshold,
            "request_rate_window_seconds": request_rate_window_seconds,
        }
        for name, value in positive_settings.items():
            if isinstance(value, bool) or not isinstance(value, int) or value < 1:
                raise ValueError(f"{name} must be a positive integer")
        self.failed_login_threshold = failed_login_threshold
        self.failed_login_window_seconds = failed_login_window_seconds
        self.request_rate_threshold = request_rate_threshold
        self.request_rate_window_seconds = request_rate_window_seconds
        self._failed_logins: dict[str, deque[float]] = defaultdict(deque)
        self._requests: dict[str, deque[float]] = defaultdict(deque)
        self._lock = Lock()
    @staticmethod
    def _client_id(client_id: str) -> str:
        if not isinstance(client_id, str) or not client_id.strip():
            raise ValueError("client_id must be a non-empty string")
        return client_id.strip()[:128]
    @staticmethod
    def _alert(
        rule: str,
        severity: str,
        client_id: str,
        reason: str,
    ) -> dict[str, Any]:
        return {
            "project": "Tamanna AI",
            "component": "IDS Detection Engine",
            "rule": rule,
            "severity": severity,
            "client_id": client_id,
            "reason": reason,
            "action": "alert_only",
            "system_firewall_modified": False,
        }
    @staticmethod
    def _prune(events: deque[float], cutoff: float) -> None:
        while events and events[0] < cutoff:
            events.popleft()
    def record_failed_login(
        self,
        client_id: str,
        now: float | None = None,
    ) -> list[dict[str, Any]]:
        """Record a failed login and alert when the threshold is reached."""
        client = self._client_id(client_id)
        current = time.monotonic() if now is None else now
        with self._lock:
            events = self._failed_logins[client]
            self._prune(events, current - self.failed_login_window_seconds)
            events.append(current)
            count = len(events)
            if count < self.failed_login_threshold:
                return []
            # Avoid emitting a new alert for every failure after the threshold.
            if count > self.failed_login_threshold:
                return []
        return [
            self._alert(
                "repeated_failed_logins",
                "high",
                client,
                f"{count} failed login attempts within "
                f"{self.failed_login_window_seconds} seconds",
            )
        ]
    def record_request(
        self,
        client_id: str,
        path: str = "/",
        now: float | None = None,
    ) -> list[dict[str, Any]]:
        """Record a request and return any matching detection alerts."""
        client = self._client_id(client_id)
        if not isinstance(path, str) or len(path) > 2048:
            return [
                self._alert(
                    "malformed_request_path",
                    "medium",
                    client,
                    "Request path is invalid or too long",
                )
            ]
        current = time.monotonic() if now is None else now
        alerts: list[dict[str, Any]] = []
        normalized_path = path.strip().lower().split("?", 1)[0]
        suspicious_markers = (
            "/.env",
            "/.git",
            "/wp-admin",
            "/wp-login.php",
            "/etc/passwd",
            "/phpmyadmin",
        )
        if "\x00" in normalized_path or "\\" in normalized_path:
            alerts.append(
                self._alert(
                    "malformed_request_path",
                    "medium",
                    client,
                    "Request path contains an invalid character",
                )
            )
        if any(marker in normalized_path for marker in suspicious_markers):
            alerts.append(
                self._alert(
                    "suspicious_path",
                    "medium",
                    client,
                    "Request targets a commonly sensitive path",
                )
            )
        with self._lock:
            events = self._requests[client]
            self._prune(events, current - self.request_rate_window_seconds)
            events.append(current)
            count = len(events)
            if count == self.request_rate_threshold + 1:
                alerts.append(
                    self._alert(
                        "high_request_rate",
                        "medium",
                        client,
                        f"More than {self.request_rate_threshold} requests "
                        f"within {self.request_rate_window_seconds} seconds",
                    )
                )
        return alerts
    def health(self) -> dict[str, Any]:
        """Return a read-only health summary."""
        with self._lock:
            clients_tracked = len(
                set(self._failed_logins) | set(self._requests)
            )
        return {
            "project": "Tamanna AI",
            "component": "IDS Detection Engine",
            "status": "OK",
            "mode": "monitor_only",
            "clients_tracked": clients_tracked,
            "system_firewall_modified": False,
        }