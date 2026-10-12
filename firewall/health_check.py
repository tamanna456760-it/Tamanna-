"""
Tamanna AI Firewall - Health Check
Owner: HM INSAN ALI
Performs read-only checks on required firewall files.
Does not modify system firewall rules.
"""
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
FIREWALL_DIR = Path(__file__).resolve().parent
REQUIRED_FILES = (
    "firewall_config.json",
    "firewall_manager.py",
    "access_control.py",
    "api_protection.py",
    "audit_log.py",
    "rate_limiter.py",
    "threat_detector.py",
    "security_monitor.py",
    "policy_validator.py",
    "security_baseline.py",
)
def check_file(path: Path) -> dict[str, Any]:
    """Check whether a required path exists and is a regular file."""
    exists = path.is_file()
    return {
        "name": path.name,
        "exists": exists,
        "status": "OK" if exists else "MISSING",
    }
def run_health_check(
    firewall_dir: str | Path = FIREWALL_DIR,
) -> dict[str, Any]:
    """Return a health report without changing checked files."""
    root = Path(firewall_dir)
    file_checks = [
        check_file(root / filename)
        for filename in REQUIRED_FILES
    ]
    config_path = root / "firewall_config.json"
    config_status = "NOT_CHECKED"
    if config_path.is_file():
        try:
            with config_path.open("r", encoding="utf-8") as file:
                config = json.load(file)
            if not isinstance(config, dict):
                config_status = "INVALID"
            else:
                config_status = "OK"
        except (OSError, json.JSONDecodeError):
            config_status = "INVALID"
    missing_count = sum(
        1 for item in file_checks if not item["exists"]
    )
    healthy = missing_count == 0 and config_status == "OK"
    return {
        "project": "Tamanna AI",
        "owner": "HM INSAN ALI",
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "status": "HEALTHY" if healthy else "NEEDS_ATTENTION",
        "firewall_directory": str(root),
        "required_files_checked": len(file_checks),
        "missing_files": missing_count,
        "configuration_status": config_status,
        "system_firewall_modified": False,
        "files": file_checks,
        "note": (
            "File and JSON checks only. This does not verify live traffic, "
            "network protection, or operating-system firewall status."
        ),
    }
def main() -> int:
    report = run_health_check()
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report["status"] == "HEALTHY" else 1
if __name__ == "__main__":
    raise SystemExit(main())