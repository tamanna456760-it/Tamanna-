"""Read-only process inventory for Tamanna AI Endpoint Security.
Owner: HM INSAN ALI
This module does not terminate processes or change system settings.
Requires the optional psutil package for process enumeration.
"""
from __future__ import annotations
from typing import Any
class ProcessMonitor:
    """Collect a limited inventory of running processes."""
    def __init__(self, config: dict[str, Any]):
        self.config = config or {}
        self.settings = self.config.get("process_monitoring", {})
        self.enabled = self.config.get("monitoring", {}).get(
            "process_monitoring", True
        )
        self.allowlist = {
            str(item).strip().lower()
            for item in self.settings.get("allowlist", [])
            if isinstance(item, str) and item.strip()
        }
    def collect(self) -> dict[str, Any]:
        """Return process inventory without command lines or environment."""
        if not self.enabled:
            return {
                "status": "disabled",
                "processes": [],
                "alerts": [],
            }
        try:
            import psutil
        except ImportError:
            return {
                "status": "unavailable",
                "processes": [],
                "alerts": [],
                "reason": "Install psutil to enable process monitoring.",
            }
        processes = []
        alerts = []
        for process in psutil.process_iter(
            attrs=["pid", "name", "exe", "status"]
        ):
            try:
                info = process.info
                name = info.get("name") or "unknown"
                executable = info.get("exe")
                record = {
                    "pid": info.get("pid"),
                    "name": name,
                    "executable": executable,
                    "status": info.get("status"),
                }
                processes.append(record)
                identity = (executable or name).strip().lower()
                if (
                    self.settings.get("alert_on_unknown_executables", True)
                    and identity not in self.allowlist
                    and name.strip().lower() not in self.allowlist
                ):
                    alerts.append({
                        "type": "executable_not_allowlisted",
                        "pid": info.get("pid"),
                        "name": name,
                        "severity": "review",
                    })
            except (
                psutil.NoSuchProcess,
                psutil.AccessDenied,
                psutil.ZombieProcess,
            ):
                # Processes can exit or become inaccessible during scanning.
                continue
        return {
            "status": "ok",
            "process_count": len(processes),
            "processes": processes,
            "alerts": alerts,
        }