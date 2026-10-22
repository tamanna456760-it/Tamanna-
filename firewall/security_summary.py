"""
Tamanna AI Firewall - Security Summary
Owner: HM INSAN ALI
Creates a read-only summary of firewall security reports.
"""
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from firewall.report_validator import validate_report_file
def build_security_summary(
    report_path: str | Path,
) -> dict[str, Any]:
    """Build a security summary from an existing event report."""
    path = Path(report_path)
    validation = validate_report_file(path)
    summary = {
        "project": "Tamanna AI",
        "owner": "HM INSAN ALI",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "report_available": path.is_file(),
        "report_valid": validation["valid"],
        "validation_errors": validation["errors"],
        "total_events": None,
        "high_risk_events": None,
        "system_firewall_modified": False,
    }
    if not validation["valid"]:
        summary["status"] = "REPORT_INVALID_OR_UNAVAILABLE"
        return summary
    try:
        with path.open("r", encoding="utf-8") as file:
            report = json.load(file)
    except (OSError, json.JSONDecodeError) as exc:
        summary["status"] = "REPORT_READ_ERROR"
        summary["validation_errors"] = [str(exc)]
        return summary
    analysis = report["analysis"]
    summary["total_events"] = analysis["total_events"]
    summary["high_risk_events"] = analysis["high_risk_events"]
    if analysis["high_risk_events"] > 0:
        summary["status"] = "REVIEW_REQUIRED"
    else:
        summary["status"] = "NO_HIGH_RISK_EVENTS_REPORTED"
    # This module does not change or verify operating-system firewall rules.
    summary["system_firewall_modified"] = False
    return summary
def save_security_summary(
    report_path: str | Path,
    output_path: str | Path,
) -> dict[str, Any]:
    """Save a summary JSON file using an atomic replacement."""
    summary = build_security_summary(report_path)
    destination = Path(output_path)
    temporary = destination.with_name(destination.name + ".tmp")
    try:
        destination.parent.mkdir(parents=True, exist_ok=True)
        with temporary.open("w", encoding="utf-8") as file:
            json.dump(summary, file, indent=2)
            file.write("\n")
        temporary.replace(destination)
        summary["saved_to"] = str(destination)
        return summary
    except OSError as exc:
        try:
            temporary.unlink(missing_ok=True)
        except OSError:
            pass
        summary["save_error"] = str(exc)
        return summary
if __name__ == "__main__":
    base_dir = Path(__file__).parent
    result = save_security_summary(
        report_path=base_dir / "reports" / "event_report.json",
        output_path=base_dir / "reports" / "security_summary.json",
    )
    print(json.dumps(result, indent=2))