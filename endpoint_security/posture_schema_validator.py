#!/usr/bin/env python3
"""Validate Tamanna AI security posture reports against JSON Schema.
Owner: HM INSAN ALI
Read-only validation. This module does not modify reports.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from typing import Any
try:
    from jsonschema import Draft202012Validator, FormatChecker
    from jsonschema.exceptions import SchemaError
except ImportError:
    Draft202012Validator = None
    FormatChecker = None
    SchemaError = Exception
BASE_DIR = Path(__file__).resolve().parent
DEFAULT_SCHEMA = BASE_DIR / "security_posture_schema.json"
def validate_posture_report(
    report_path: Path,
    schema_path: Path = DEFAULT_SCHEMA,
) -> dict[str, Any]:
    """Validate one report against the configured JSON Schema."""
    if Draft202012Validator is None:
        return {
            "valid": False,
            "status": "DEPENDENCY_MISSING",
            "errors": [
                "Install the jsonschema package to enable schema validation."
            ],
            "read_only": True,
        }
    try:
        with schema_path.open("r", encoding="utf-8") as handle:
            schema = json.load(handle)
        with report_path.open("r", encoding="utf-8") as handle:
            report = json.load(handle)
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        return {
            "valid": False,
            "status": "ERROR",
            "report_path": str(report_path),
            "schema_path": str(schema_path),
            "errors": [f"{type(exc).__name__}: {exc}"],
            "read_only": True,
        }
    if not isinstance(schema, dict):
        return {
            "valid": False,
            "status": "INVALID_SCHEMA",
            "errors": ["Schema root must be a JSON object."],
            "read_only": True,
        }
    try:
        Draft202012Validator.check_schema(schema)
        validator = Draft202012Validator(
            schema,
            format_checker=FormatChecker(),
        )
        validation_errors = sorted(
            validator.iter_errors(report),
            key=lambda error: list(map(str, error.absolute_path)),
        )
    except SchemaError as exc:
        return {
            "valid": False,
            "status": "INVALID_SCHEMA",
            "errors": [str(exc)],
            "read_only": True,
        }
    errors = [
        {
            "path": "/" + "/".join(
                str(part) for part in error.absolute_path
            ),
            "message": error.message,
        }
        for error in validation_errors
    ]
    return {
        "valid": not errors,
        "status": "VALID" if not errors else "INVALID",
        "project": "Tamanna AI",
        "owner": "HM INSAN ALI",
        "report_path": str(report_path),
        "schema_path": str(schema_path),
        "error_count": len(errors),
        "errors": errors,
        "read_only": True,
        "note": (
            "Schema validation checks report structure only. "
            "It does not prove report authenticity or system security."
        ),
    }
def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate a Tamanna AI posture report."
    )
    parser.add_argument("report", type=Path)
    parser.add_argument(
        "--schema",
        type=Path,
        default=DEFAULT_SCHEMA,
    )
    args = parser.parse_args()
    result = validate_posture_report(args.report, args.schema)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    if result["status"] == "VALID":
        return 0
    if result["status"] == "DEPENDENCY_MISSING":
        return 3
    return 1 if result["status"] == "INVALID" else 2
if __name__ == "__main__":
    raise SystemExit(main())