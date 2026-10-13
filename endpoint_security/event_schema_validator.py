#!/usr/bin/env python3
"""Validate the structure of Tamanna AI Endpoint Security events.
Owner: HM INSAN ALI
Read-only validation. Does not alter logs or take enforcement actions.
"""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path
from typing import Any
DEFAULT_LOG = Path("data/endpoint_security_events.jsonl")
MAX_LINE_BYTES = 16 * 1024
MAX_STRING_LENGTH = 4096
REQUIRED_FIELDS = ("event_type", "timestamp")
def validate_event(event: Any) -> list[str]:
    """Return validation errors for one event record."""
    errors: list[str] = []
    if not isinstance(event, dict):
        return ["record must be a JSON object"]
    for field in REQUIRED_FIELDS:
        value = event.get(field)
        if not isinstance(value, str) or not value.strip():
            errors.append(f"{field} must be a non-empty string")
        elif len(value) > MAX_STRING_LENGTH:
            errors.append(f"{field} exceeds maximum length")
    severity = event.get("severity")
    if severity is not None:
        allowed_severities = {"info", "low", "medium", "high", "critical"}
        if not isinstance(severity, str):
            errors.append("severity must be a string")
        elif severity.lower() not in allowed_severities:
            errors.append("severity is not a recognized value")
    return errors
def validate_log(log_path: Path) -> dict[str, Any]:
    valid = 0
    invalid = 0
    oversized = 0
    issues: list[dict[str, Any]] = []
    with log_path.open("rb") as log_file:
        for line_number, raw_line in enumerate(log_file, start=1):
            if not raw_line.strip():
                continue
            if len(raw_line) > MAX_LINE_BYTES:
                oversized += 1
                invalid += 1
                issues.append({
                    "line": line_number,
                    "errors": ["line exceeds maximum permitted size"],
                })
                continue
            try:
                text = raw_line.decode("utf-8")
                event = json.loads(text)
            except (UnicodeDecodeError, json.JSONDecodeError):
                invalid += 1
                issues.append({
                    "line": line_number,
                    "errors": ["invalid UTF-8 or JSON"],
                })
                continue
            errors = validate_event(event)
            if errors:
                invalid += 1
                issues.append({
                    "line": line_number,
                    "errors": errors,
                })
            else:
                valid += 1
    return {
        "project": "Tamanna AI",
        "owner": "HM INSAN ALI",
        "component": "Endpoint Security",
        "report_type": "event_schema_validation",
        "valid_records": valid,
        "invalid_records": invalid,
        "oversized_records": oversized,
        "issues": issues,
        "status": "PASS" if invalid == 0 else "FAIL",
    }
def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate Endpoint Security event log structure."
    )
    parser.add_argument(
        "--log",
        type=Path,
        default=DEFAULT_LOG,
        help="Path to the JSONL event log.",
    )
    args = parser.parse_args()
    try:
        report = validate_log(args.log)
    except OSError as exc:
        print(f"ERROR: Cannot read log ({exc.__class__.__name__}).")
        return 2
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report["status"] == "PASS" else 1
if __name__ == "__main__":
    sys.exit(main())