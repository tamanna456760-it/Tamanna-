"""Health checks for Tamanna AI Endpoint Security.
Owner: HM INSAN ALI
Checks configuration and component initialization only.
Does not perform enforcement actions.
"""
from __future__ import annotations
import json
from pathlib import Path
from typing import Any
from .manager import EndpointSecurityManager
def run_health_check(
    config_path: str | Path = "endpoint_security/endpoint_config.json",
) -> dict[str, Any]:
    """Load configuration and return a health-check result."""
    path = Path(config_path)
    try:
        with path.open("r", encoding="utf-8") as file_handle:
            config = json.load(file_handle)
        if not isinstance(config, dict):
            raise ValueError("Configuration root must be a JSON object")
        if config.get("project") != "Tamanna AI":
            raise ValueError("Unexpected project name")
        if config.get("mode") != "monitor_only":
            raise ValueError("Only monitor_only mode is supported")
        enforcement = config.get("enforcement", {})
        if not isinstance(enforcement, dict):
            raise ValueError("enforcement must be a JSON object")
        unsafe_flags = (
            "kill_processes",
            "quarantine_files",
            "delete_files",
            "modify_system_settings",
        )
        if any(enforcement.get(flag, False) for flag in unsafe_flags):
            raise ValueError("Enforcement options must remain disabled")
        manager = EndpointSecurityManager(config)
        result = manager.health()
        if result.get("status") not in {"healthy", "disabled"}:
            raise RuntimeError("Endpoint Security health check failed")
        return {
            "status": result["status"],
            "project": "Tamanna AI",
            "component": "Endpoint Security",
            "mode": "monitor_only",
            "config_path": str(path),
            "enforcement_enabled": False,
            "details": result,
        }
    except (
        OSError,
        json.JSONDecodeError,
        ValueError,
        TypeError,
        RuntimeError,
    ) as exc:
        return {
            "status": "unhealthy",
            "project": "Tamanna AI",
            "component": "Endpoint Security",
            "config_path": str(path),
            "error": str(exc),
        }
if __name__ == "__main__":
    import sys
    config_argument = (
        sys.argv[1]
        if len(sys.argv) > 1
        else "endpoint_security/endpoint_config.json"
    )
    report = run_health_check(config_argument)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    raise SystemExit(0 if report["status"] in {"healthy", "disabled"} else 1)