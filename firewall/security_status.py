"""
Tamanna AI Firewall - Security Status
Owner: HM INSAN ALI
Read-only status overview for firewall configuration and reports.
"""
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
def check_security_status(
    base_dir: str | Path | None = None,
) -> dict[str, Any]:
    """Check the availability and basic validity of security files."""
    root = Path(base_dir) if base_dir is not None else Path(__file__).parent
    config_path = root / "firewall_config.json"
    event_report_path = root / "reports" / "event_report.json"
    summary_path = root / "reports" / "security_summary.json"
    checks = {
        "config_exists": config_path.is_file(),
        "event_report_exists": event_report_path.is_file(),
        "security_summary_exists": summary_path.is_file(),
    }
    config_mode = None
    config_valid = False
    config_errors = []
    if checks["config_exists"]:
        try:
            with config_path.open("r", encoding="utf-8") as file:
                config = json.load(file)
            config_mode = config.get("mode")
            config_valid = (
                isinstance(config, dict)
                and config_mode in {"audit_only", "monitor", "enforce"}
                and isinstance(config.get("allowed_ips", []), list)
                and isinstance(config.get("allowed_ports", []), list)
            )
            if not config_valid:
                config_errors.append("Configuration fields are invalid.")
        except (OSError, json.JSONDecodeError) as exc:
            config_errors.append(str(exc))
    checks["config_valid"] = config_valid
    return {
        "project": "Tamanna AI",
        "owner": "HM INSAN ALI",
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "status": (
            "READY_FOR_REVIEW"
            if all(checks.values())
            else "INCOMPLETE"
        ),
        "config_mode": config_mode,
        "checks": checks,
        "config_errors": config_errors,
        "system_firewall_modified": False,
        "note": (
            "This is a file and configuration check only. "
            "It does not verify live traffic filtering or operating-system rules."
        ),
    }
def save_security_status(
    output_path: str | Path,
    base_dir: str | Path | None = None,
) -> dict[str, Any]:
    """Save the status report as JSON."""
    result = check_security_status(base_dir)
    destination = Path(output_path)
    temporary = destination.with_name(destination.name + ".tmp")
    try:
        destination.parent.mkdir(parents=True, exist_ok=True)
        with temporary.open("w", encoding="utf-8") as file:
            json.dump(result, file, indent=2)
            file.write("\n")
        temporary.replace(destination)
        result["saved_to"] = str(destination)
    except OSError as exc:
        try:
            temporary.unlink(missing_ok=True)
        except OSError:
            pass
        result["save_error"] = str(exc)
    return result
if __name__ == "__main__":
    root = Path(__file__).parent
    output = root / "reports" / "security_status.json"
    print(json.dumps(save_security_status(output), indent=2))