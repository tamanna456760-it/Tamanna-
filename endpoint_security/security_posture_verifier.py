#!/usr/bin/env python3
"""Verify the structure and consistency of Tamanna AI posture reports.
Owner: HM INSAN ALI
Read-only verification. This does not prove report authenticity or
cryptographic integrity.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from typing import Any
PROJECT_NAME = "Tamanna AI"
OWNER = "HM INSAN ALI"
VALID_CHECK_STATUSES = {
    "PASS", "PASSED", "OK",
    "FAIL", "FAILED",
    "ERROR", "UNKNOWN",
}
def verify_posture_report(report_path: Path) -> dict[str, Any]:
    """Validate report fields and recompute check totals."""
    try:
        with report_path.open("r", encoding="utf-8") as handle:
            report = json.load(handle)
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        return {
            "valid": False,
            "status": "ERROR",
            "report_path": str(report_path),
            "errors": [f"{type(exc).__name__}: {exc}"],
            "read_only": True,
        }
    if not isinstance(report, dict):
        return {
            "valid": False,
            "status": "INVALID",
            "report_path": str(report_path),
            "errors": ["Report root must be a JSON object."],
            "read_only": True,
        }
    errors: list[str] = []
    if report.get("project") != PROJECT_NAME:
        errors.append("Incorrect or missing project name.")
    if report.get("owner") != OWNER:
        errors.append("Incorrect or missing owner.")
    if not isinstance(report.get("generated_at_utc"), str):
        errors.append("Missing generated_at_utc timestamp.")
    checks = report.get("checks")
    if not isinstance(checks, list):
        errors.append("checks must be a list.")
        checks = []
    counts = {
        "checks_passed": 0,
        "checks_failed": 0,
        "checks_error": 0,
    }
    for index, check in enumerate(checks):
        if not isinstance(check, dict):
            errors.append(f"Check at index {index} must be an object.")
            counts["checks_error"] += 1
            continue
        status = check.get("status")
        if not isinstance(status, str):
            errors.append(f"Check at index {index} has no valid status.")
            counts["checks_error"] += 1
            continue
        status = status.upper()
        if status not in VALID_CHECK_STATUSES:
            errors.append(f"Check at index {index} has unknown status.")
            counts["checks_error"] += 1
        elif status in {"PASS", "PASSED", "OK"}:
            counts["checks_passed"] += 1
        elif status in {"FAIL", "FAILED"}:
            counts["checks_failed"] += 1
        else:
            counts["checks_error"] += 1
    # These values should match the source report's own summary.
    for key, actual in counts.items():
        if report.get(key) != actual:
            errors.append(
                f"{key} mismatch: expected {actual}, "
                f"found {report.get(key)!r}."
            )
    if errors:
        status = "INVALID"
    elif counts["checks_failed"] or counts["checks_error"]:
        status = "REVIEW_REQUIRED"
    else:
        status = "VALID"
    return {
        "valid": not errors,
        "status": status,
        "report_path": str(report_path),
        "checks_total": len(checks),
        **counts,
        "errors": errors,
        "read_only": True,
        "note": (
            "Structural consistency only; this does not establish "
            "that the report is authentic or that the system is secure."
        ),
    }
def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify a Tamanna AI security posture report."
    )
    parser.add_argument(
        "report",
        type=Path,
        help="Path to an existing security posture JSON report.",
    )
    args = parser.parse_args()
    result = verify_posture_report(args.report)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    if result["status"] == "VALID":
        return 0
    if result["status"] == "REVIEW_REQUIRED":
        return 1
    return 2
if __name__ == "__main__":
    raise SystemExit(main())