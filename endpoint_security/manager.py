"""Coordinator for Tamanna AI Endpoint Security.
Owner: HM INSAN ALI
Monitor-only implementation. No process termination, file deletion,
quarantine, or operating-system configuration changes are performed.
"""
from __future__ import annotations
from typing import Any
from .event_logger import EndpointEventLogger
from .file_integrity import FileIntegrityMonitor
from .process_monitor import ProcessMonitor
class EndpointSecurityManager:
    """Coordinate endpoint inventory, integrity checks, and event logging."""
    def __init__(self, config: dict[str, Any]):
        if not isinstance(config, dict):
            raise TypeError("Endpoint security config must be a dictionary")
        self.config = config
        self.enabled = config.get("enabled", True)
        self.mode = config.get("mode", "monitor_only")
        if self.mode != "monitor_only":
            raise ValueError(
                "Only monitor_only mode is supported by this implementation"
            )
        enforcement = config.get("enforcement", {})
        forbidden_options = (
            "kill_processes",
            "quarantine_files",
            "delete_files",
            "modify_system_settings",
        )
        if any(enforcement.get(option, False) for option in forbidden_options):
            raise ValueError(
                "Enforcement actions must remain disabled"
            )
        self.process_monitor = ProcessMonitor(config)
        self.file_integrity = FileIntegrityMonitor(config)
        self.event_logger = EndpointEventLogger(config)
    def health(self) -> dict[str, Any]:
        """Report configuration-level health without scanning the host."""
        if not self.enabled:
            return {
                "status": "disabled",
                "mode": self.mode,
            }
        return {
            "status": "healthy",
            "project": "Tamanna AI",
            "component": "Endpoint Security",
            "mode": "monitor_only",
            "process_monitoring": self.config.get(
                "monitoring", {}
            ).get("process_monitoring", True),
            "file_integrity_monitoring": self.config.get(
                "file_integrity", {}
            ).get("enabled", True),
            "enforcement_enabled": False,
        }
    def scan_processes(self) -> dict[str, Any]:
        """Collect process inventory and log summary findings."""
        if not self.enabled:
            return {"status": "disabled", "processes": [], "alerts": []}
        result = self.process_monitor.collect()
        if result.get("alerts"):
            self.event_logger.log_event({
                "event_type": "process_monitoring_findings",
                "alert_count": len(result["alerts"]),
                "alerts": result["alerts"],
            })
        return result
    def check_file(self, path: str) -> dict[str, Any]:
        """Calculate the hash of one explicitly selected file."""
        if not self.enabled:
            return {"status": "disabled", "path": path}
        result = self.file_integrity.hash_file(path)
        if result.get("status") in {"error", "skipped"}:
            self.event_logger.log_event({
                "event_type": "file_integrity_check",
                "result": result,
            })
        return result
    def compare_file(
        self,
        path: str,
        baseline_sha256: str,
    ) -> dict[str, Any]:
        """Compare a selected file against a supplied trusted baseline."""
        if not self.enabled:
            return {"status": "disabled", "path": path}
        result = self.file_integrity.compare(path, baseline_sha256)
        if result.get("status") in {"changed", "error", "skipped"}:
            self.event_logger.log_event({
                "event_type": "file_integrity_finding",
                "result": result,
            })
        return result