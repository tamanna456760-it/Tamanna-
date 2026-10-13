#!/usr/bin/env python3
"""Read-only verifier for Tamanna AI security audit reports.
Owner: HM INSAN ALI
"""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path
VALID_STATUSES = {"PASS", "FAIL", "ERROR"}
def verify_report(report_path: Path) -> dict:
    """Validate the structure and internal consistency of an audit report."""
    try:
        with report_path.open("r", encoding="utf-8") as handle:
            report = json.load(handle)
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        return {
            "valid": False,
            "errors": [f"Cannot read valid JSON report: {exc}"],
        }
    errors = []
    if not isinstance(report, dict):
        return {
            "valid": False,
            "errors": ["Report root must be a JSON object."],
        }
    if report.get("project") != "Tamanna AI":
        errors.append("Unexpected project name.")
    if report.get("owner") != "HM INSAN ALI":
        errors.append("Unexpected owner.")
    if report.get("mode") != "read_only":
        errors.append("Report mode must be read_only.")
    checks = report.get("checks")
    summary = report.get("summary")
    if not isinstance(checks, list):
        errors.append("'checks' must be a list.")
        checks = []
    if not isinstance(summary, dict):
        errors.append("'summary' must be an object.")
        summary = {}
    statuses = []
    for index, check in enumerate(checks):
        if not isinstance(check, dict):
            errors.append(f"Check {index} must be an object.")
            continue
        status = check.get("status")
        if status not in VALID_STATUSES:
            errors.append(f"Check {index} has an invalid status.")
        else:
            statuses.append(status)
        if not isinstance(check.get("check"), str) or not check["check"].strip():
            errors.append(f"Check {index} has no valid name.")
        if "details" not in check:
            errors.append(f"Check {index} is missing details.")
    expected = {
        "total": len(checks),
        "passed": statuses.count("PASS"),
        "failed": statuses.count("FAIL"),
        "errors": statuses.count("ERROR"),
    }
    for key, value in expected.items():
        if summary.get(key) != value:
            errors.append(
                f"Summary mismatch for {key}: "
                f"expected {value}, got {summary.get(key)!r}."
            )
    expected_overall = (
        "PASS"
        if checks
        and len(statuses) == len(checks)
        and all(status == "PASS" for status in statuses)
        else "REVIEW_REQUIRED"
    )
    if summary.get("overall_status") != expected_overall:
        errors.append("Overall status does not match the check results.")
    return {
        "valid": not errors,
        "report": str(report_path),
        "checks_verified": len(checks),
        "errors": errors,
        "note": (
            "Structural validation only; this does not prove report "
            "authenticity or that the system is malware-free."
        ),
    }
def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify a Tamanna AI security audit report."
    )
    parser.add_argument(
        "report",
        type=Path,
        help="Path to the JSON audit report.",
    )
    args = parser.parse_args()
    result = verify_report(args.report)
    print(json.dumps(result, indent=2))
    return 0 if result["valid"] else 1
if __name__ == "__main__":
    sys.exit(main())