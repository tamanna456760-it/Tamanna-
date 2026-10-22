File: ids/health_check.py

"""
Tamanna AI IDS Health Check.
Project: Tamanna AI
Owner: HM INSAN ALI
Checks IDS component availability without modifying system settings.
"""
from __future__ import annotations
from datetime import datetime, timezone
from typing import Any
from ids.ids_manager import IDSManager
def run_health_check(
    manager: IDSManager | None = None,
) -> dict[str, Any]:
    """Check IDS component health and return a structured report."""
    if manager is None:
        manager = IDSManager()
    checked_at = datetime.now(timezone.utc).isoformat()
    components: dict[str, Any] = {}
    errors: list[str] = []
    checks = {
        "collector": manager.collector.health,
        "detector": manager.detector.health,
        "alerts": manager.alert_manager.summary,
    }
    for name, check in checks.items():
        try:
            result = check()
            if not isinstance(result, dict):
                raise TypeError("Health result must be a dictionary")
            components[name] = {
                "status": "ok",
                "details": result,
            }
        except Exception as exc:
            components[name] = {
                "status": "error",
                "error": str(exc),
            }
            errors.append(name)
    healthy = not errors
    return {
        "project": "Tamanna AI",
        "owner": "HM INSAN ALI",
        "checked_at": checked_at,
        "status": "healthy" if healthy else "degraded",
        "enabled": manager.enabled,
        "mode": manager.mode,
        "components": components,
        "failed_components": errors,
        "automatic_ip_blocking": False,
        "system_firewall_modified": False,
    }
if __name__ == "__main__":
    import json
    report = run_health_check()
    print(json.dumps(report, indent=2, ensure_ascii=False))
    raise SystemExit(
        0 if report["status"] == "healthy" else 1
    )