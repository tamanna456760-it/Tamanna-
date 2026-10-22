#!/usr/bin/env python3
"""Build a consistent Tamanna AI security posture report.
Owner: HM INSAN ALI
This module summarizes supplied check results only.
It does not execute scans or change system settings.
"""
from __future__ import annotations
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
PROJECT_NAME = "Tamanna AI"
OWNER = "HM INSAN ALI"
PASS_STATUSES = {"PASS", "PASSED", "OK"}
FAIL_STATUSES = {"FAIL", "FAILED"}
def build_posture_report(
    checks: list[dict[str, Any]],
) -> dict[str, Any]:
    """Build a report with consistent status counts."""
    normalized_checks: list[dict[str, Any]] = []
    passed = 0
    failed = 0
    errors = 0
    for index, check in enumerate(checks):
        if not isinstance(check, dict):
            normalized_checks.append({
                "name": f"check_{index + 1}",
                "status": "ERROR",
                "details": "Check result must be a JSON object.",
            })
            errors += 1
            continue
        name = check.get("name")
        raw_status = check.get("status")
        if not isinstance(name, str) or not name.strip():
            name = f"check_{index + 1}"
        if not isinstance(raw_status, str):
            status = "ERROR"
        else:
            candidate = raw_status.upper()
            if candidate in PASS_STATUSES:
                status = "PASS"
            elif candidate in FAIL_STATUSES:
                status = "FAIL"
            elif candidate in {"ERROR", "UNKNOWN"}:
                status = candidate
            else:
                status = "ERROR"
        item: dict[str, Any] = {
            "name": name,
            "status": status,
        }
        details = check.get("details")
        if isinstance(details, str):
            item["details"] = details
        normalized_checks.append(item)
        if status == "PASS":
            passed += 1
        elif status == "FAIL":
            failed += 1
        else:
            errors += 1
    if failed or errors:
        report_status = "REVIEW_REQUIRED"
    else:
        report_status = "VALID"
    return {
        "project": PROJECT_NAME,
        "owner": OWNER,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": report_status,
        "checks": normalized_checks,
        "checks_passed": passed,
        "checks_failed": failed,
        "checks_error": errors,
        "read_only": True,
        "note": (
            "This report summarizes supplied results only. "
            "It does not prove the system is secure."
        ),
    }
def load_checks(input_path: Path) -> list[dict[str, Any]]:
    """Load check results from a JSON array."""
    with input_path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, list):
        raise ValueError("Input must be a JSON array of check objects.")
    if any(not isinstance(item, dict) for item in data):
        raise ValueError("Every input check must be a JSON object.")
    return data
def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build a Tamanna AI security posture report."
    )
    parser.add_argument(
        "--input",
        type=Path,
        required=True,
        help="JSON file containing a list of check results.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="New report output path. Existing files are not overwritten.",
    )
    args = parser.parse_args()
    try:
        checks = load_checks(args.input)
        report = build_posture_report(checks)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("x", encoding="utf-8") as handle:
            json.dump(report, handle, indent=2, ensure_ascii=False)
            handle.write("\n")
    except FileExistsError:
        print(f"ERROR: Output already exists: {args.output}")
        return 2
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        print(f"ERROR: {type(exc).__name__}: {exc}")
        return 2
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 1 if report["status"] == "REVIEW_REQUIRED" else 0
if __name__ == "__main__":
    raise SystemExit(main())