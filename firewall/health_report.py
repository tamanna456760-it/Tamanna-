"""
Tamanna AI Firewall - Health Report
Owner: HM INSAN ALI
Runs read-only health checks and saves a JSON report.
"""
import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from firewall.health_check import run_health_check
FIREWALL_DIR = Path(__file__).resolve().parent
DEFAULT_REPORT_PATH = FIREWALL_DIR / "reports" / "health_report.json"
def save_health_report(
    report_path: str | Path = DEFAULT_REPORT_PATH,
    firewall_dir: str | Path = FIREWALL_DIR,
) -> dict[str, Any]:
    """Run a health check, save its result, and return the report."""
    health = run_health_check(firewall_dir)
    report = {
        "project": "Tamanna AI",
        "owner": "HM INSAN ALI",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "health": health,
        "system_firewall_modified": False,
    }
    destination = Path(report_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    temp_path = None
    try:
        # Create the temporary file in the destination directory so
        # replacement remains on the same filesystem.
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=destination.parent,
            prefix=f".{destination.name}.",
            suffix=".tmp",
            delete=False,
        ) as file:
            temp_path = Path(file.name)
            json.dump(report, file, indent=2, ensure_ascii=False)
            file.write("\n")
            file.flush()
            os.fsync(file.fileno())
        temp_path.replace(destination)
    finally:
        if temp_path is not None and temp_path.exists():
            temp_path.unlink()
    return report
def main() -> int:
    try:
        report = save_health_report()
    except (OSError, ValueError, TypeError) as exc:
        print(f"Health report generation failed: {exc}")
        return 2
    print(json.dumps(report, indent=2, ensure_ascii=False))
    print(f"\nReport saved to: {DEFAULT_REPORT_PATH}")
    return 0 if report["health"]["status"] == "HEALTHY" else 1
if __name__ == "__main__":
    raise SystemExit(main())