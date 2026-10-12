File: ids/ids_report.py

"""
Tamanna AI IDS Report Generator.
Project: Tamanna AI
Owner: HM INSAN ALI
Generates a read-only IDS status report.
No automatic blocking or system firewall changes.
"""
from __future__ import annotations
from datetime import datetime, timezone
from typing import Any
from ids.health_check import run_health_check
from ids.ids_manager import IDSManager
def generate_report(
    manager: IDSManager | None = None,
) -> dict[str, Any]:
    """Generate a structured IDS report."""
    if manager is None:
        manager = IDSManager()
    health = run_health_check(manager)
    try:
        alert_summary = manager.alert_manager.summary()
        if not isinstance(alert_summary, dict):
            alert_summary = {
                "status": "unavailable",
                "reason": "Alert summary was not a dictionary",
            }
    except Exception as exc:
        alert_summary = {
            "status": "error",
            "reason": str(exc),
        }
    return {
        "project": "Tamanna AI",
        "owner": "HM INSAN ALI",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "mode": manager.mode,
        "enabled": manager.enabled,
        "health_status": health["status"],
        "events": {
            "stored_in_memory": manager.collector.count(),
        },
        "alerts": alert_summary,
        "health_check": health,
        "enforcement": {
            "automatic_ip_blocking": False,
            "system_firewall_modified": False,
            "mode": "monitor_only",
        },
    }
if __name__ == "__main__":
    import json
    import sys
    report = generate_report()
    print(json.dumps(report, indent=2, ensure_ascii=False))
    sys.exit(
        0 if report["health_status"] == "healthy" else 1
    )