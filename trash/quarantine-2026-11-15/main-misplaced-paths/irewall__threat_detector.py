
"""
Tamanna AI — Advanced Threat Detector
Owner: HM INSAN ALI

Detects suspicious application-level activity.
Monitoring only: this module does not block IPs or modify firewall rules.
"""

from __future__ import annotations

import ipaddress
import re
import threading
import time
from collections import defaultdict, deque
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ThreatAlert:
    severity: str
    category: str
    message: str
    client_ip: str | None
    timestamp: float


class ThreatDetector:
    """Thread-safe, bounded-window detector for basic abuse signals."""

    def __init__(
        self,
        failed_login_threshold: int = 5,
        failed_login_window: int = 300,
        request_threshold: int = 120,
        request_window: int = 60,
        max_tracked_ips: int = 10000,
    ) -> None:
        for name, value in (
            ("failed_login_threshold", failed_login_threshold),
            ("failed_login_window", failed_login_window),
            ("request_threshold", request_threshold),
            ("request_window", request_window),
            ("max_tracked_ips", max_tracked_ips),
        ):
            if type(value) is not int or value < 1:
                raise ValueError(f"{name} must be a positive integer.")

        self.failed_login_threshold = failed_login_threshold
        self.failed_login_window = failed_login_window
        self.request_threshold = request_threshold
        self.request_window = request_window
        self.max_tracked_ips = max_tracked_ips

        self._failed_logins: dict[str, deque[float]] = defaultdict(deque)
        self._requests: dict[str, deque[float]] = defaultdict(deque)
        self._lock = threading.Lock()

    @staticmethod
    def _valid_ip(client_ip: str) -> bool:
        try:
            ipaddress.ip_address(client_ip)
            return True
        except (ValueError, TypeError):
            return False

    def _ensure_capacity(self, client_ip: str) -> bool:
        tracked = set(self._failed_logins) | set(self._requests)

        if client_ip in tracked:
            return True

        return len(tracked) < self.max_tracked_ips

    @staticmethod
    def _trim(events: deque[float], cutoff: float) -> None:
        while events and events[0] <= cutoff:
            events.popleft()

    def record_failed_login(
        self,
        client_ip: str,
        now: float | None = None,
    ) -> list[ThreatAlert]:
        """Record a failed login and report threshold crossings."""
        if not self._valid_ip(client_ip):
            return []

        current = time.monotonic() if now is None else now

        with self._lock:
            if not self._ensure_capacity(client_ip):
                return []

            events = self._failed_logins[client_ip]
            self._trim(events, current - self.failed_login_window)
            events.append(current)

            if len(events) == self.failed_login_threshold:
                return [
                    ThreatAlert(
                        severity="high",
                        category="repeated_failed_logins",
                        message="Failed-login threshold reached.",
                        client_ip=client_ip,
                        timestamp=current,
                    )
                ]

        return []

    def record_request(
        self,
        client_ip: str,
        now: float | None = None,
    ) -> list[ThreatAlert]:
        """Detect a high request rate from one client IP."""
        if not self._valid_ip(client_ip):
            return []

        current = time.monotonic() if now is None else now

        with self._lock:
            if not self._ensure_capacity(client_ip):
                return []

            events = self._requests[client_ip]
            self._trim(events, current - self.request_window)
            events.append(current)

            if len(events) == self.request_threshold:
                return [
                    ThreatAlert(
                        severity="medium",
                        category="high_request_rate",
                        message="Request-rate threshold reached.",
                        client_ip=client_ip,
                        timestamp=current,
                    )
                ]

        return []

    @staticmethod
    def inspect_path(path: str) -> list[ThreatAlert]:
        """
        Flag common suspicious path patterns for review.

        This is a heuristic, not proof of an attack. Do not use its
        output alone to block users.
        """
        if not isinstance(path, str):
            return []

        normalized = path[:2048].lower()

        patterns = {
            "path_traversal_attempt": r"(\.\./|%2e%2e%2f|%2e%2e/)",
            "sensitive_file_probe": r"(/\.env|/etc/passwd|/wp-config\.php)",
            "common_admin_probe": r"(/wp-admin|/phpmyadmin|/admin/login)",
        }

        findings = []

        for category, pattern in patterns.items():
            if re.search(pattern, normalized):
                findings.append(
                    ThreatAlert(
                        severity="medium",
                        category=category,
                        message="Suspicious request path requires review.",
                        client_ip=None,
                        timestamp=time.time(),
                    )
                )

        return findings


_DEFAULT_DETECTOR = ThreatDetector()


def alert_to_dict(alert: ThreatAlert) -> dict[str, Any]:
    """Convert an alert into a JSON-compatible dictionary."""
    return {
        "severity": alert.severity,
        "category": alert.category,
        "message": alert.message,
        "client_ip": alert.client_ip,
        "timestamp": alert.timestamp,
        "action_taken": "none_monitoring_only",
    }


if __name__ == "__main__":
    detector = ThreatDetector(failed_login_threshold=3)

    alerts = []
    for _ in range(3):
        alerts.extend(
            detector.record_failed_login(
                "192.0.2.10",
                now=100.0,
            )
        )

    print("Generated alerts:")
    for alert in alerts:
        print(alert_to_dict(alert))

    print("Path inspection:")
    for alert in detector.inspect_path("/../../etc/passwd"):
        print(alert_to_dict(alert))
