"""
Tamanna AI Firewall - Event Report
Owner: HM INSAN ALI
Generates a JSON report from stored security events.
This module does not block traffic or change system firewall rules.
"""
import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from firewall.event_analyzer import analyze_store
from firewall.security_event_store import SecurityEventStore
FIREWALL_DIR = Path(__file__).resolve().parent
DEFAULT_REPORT_PATH = FIREWALL_DIR / "reports" / "event_report.json"
def generate_event_report(
    report_path: str | Path = DEFAULT_REPORT_PATH,
    event_store: SecurityEventStore | None = None,
    limit: int = 1000,
) -> dict[str, Any]:
    """Analyze recent stored events and atomically save a JSON report."""
    if event_store is None:
        event_store = SecurityEventStore()
    analysis = analyze_store(store=event_store, limit=limit)
    report = {
        "project": "Tamanna AI",
        "owner": "HM INSAN ALI",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "analysis": analysis,
        "system_firewall_modified": False,
    }
    destination = Path(report_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=destination.parent,
            prefix=f".{destination.name}.",
            suffix=".tmp",
            delete=False,
        ) as file:
            temporary_path = Path(file.name)
            json.dump(report, file, indent=2, ensure_ascii=False)
            file.write("\n")
            file.flush()
            os.fsync(file.fileno())
        temporary_path.replace(destination)
    finally:
        if temporary_path is not None and temporary_path.exists():
            temporary_path.unlink()
    return report
def main() -> int:
    try:
        report = generate_event_report()
    except (OSError, ValueError, TypeError) as exc:
        print(f"Event report generation failed: {exc}")
        return 2
    print(json.dumps(report, indent=2, ensure_ascii=False))
    print(f"\nReport saved to: {DEFAULT_REPORT_PATH}")
    return 0
if __name__ == "__main__":
    raise SystemExit(main())