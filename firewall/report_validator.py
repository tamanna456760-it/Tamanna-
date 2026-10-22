"""
Tamanna AI Firewall - Security Report Validator
Owner: HM INSAN ALI
Validates security report structure without changing system settings.
"""
import json
from pathlib import Path
from typing import Any
REQUIRED_FIELDS = {
    "project",
    "owner",
    "generated_at",
    "analysis",
    "system_firewall_modified",
}
def validate_report(report: Any) -> dict:
    """Validate the structure and basic types of a security report."""
    errors = []
    if not isinstance(report, dict):
        return {
            "valid": False,
            "errors": ["Report must be a JSON object."],
        }
    missing = sorted(REQUIRED_FIELDS - report.keys())
    if missing:
        errors.append(
            "Missing required fields: " + ", ".join(missing)
        )
    if "project" in report and report["project"] != "Tamanna AI":
        errors.append("Invalid project name.")
    if "owner" in report and report["owner"] != "HM INSAN ALI":
        errors.append("Invalid owner.")
    if "generated_at" in report and not isinstance(
        report["generated_at"], str
    ):
        errors.append("'generated_at' must be a string.")
    if "analysis" in report:
        analysis = report["analysis"]
        if not isinstance(analysis, dict):
            errors.append("'analysis' must be a JSON object.")
        else:
            total = analysis.get("total_events")
            high_risk = analysis.get("high_risk_events")
            if (
                not isinstance(total, int)
                or isinstance(total, bool)
                or total < 0
            ):
                errors.append(
                    "'analysis.total_events' must be a non-negative integer."
                )
            if (
                not isinstance(high_risk, int)
                or isinstance(high_risk, bool)
                or high_risk < 0
            ):
                errors.append(
                    "'analysis.high_risk_events' must be a non-negative integer."
                )
            if (
                isinstance(total, int)
                and not isinstance(total, bool)
                and isinstance(high_risk, int)
                and not isinstance(high_risk, bool)
                and high_risk > total
            ):
                errors.append(
                    "High-risk events cannot exceed total events."
                )
    if "system_firewall_modified" in report:
        if not isinstance(report["system_firewall_modified"], bool):
            errors.append(
                "'system_firewall_modified' must be true or false."
            )
    return {
        "valid": not errors,
        "errors": errors,
    }
def validate_report_file(file_path: str | Path) -> dict:
    """Read and validate a JSON report file."""
    path = Path(file_path)
    try:
        with path.open("r", encoding="utf-8") as file:
            report = json.load(file)
    except FileNotFoundError:
        return {
            "valid": False,
            "errors": ["Report file not found."],
        }
    except (json.JSONDecodeError, OSError) as exc:
        return {
            "valid": False,
            "errors": [f"Unable to read report: {exc}"],
        }
    return validate_report(report)
if __name__ == "__main__":
    default_path = (
        Path(__file__).parent
        / "reports"
        / "event_report.json"
    )
    result = validate_report_file(default_path)
    print(json.dumps(result, indent=2))
    if not result["valid"]:
        raise SystemExit(1)