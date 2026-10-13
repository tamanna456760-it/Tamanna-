#!/usr/bin/env python3
"""Validate Tamanna AI posture archive preflight results.
Owner: HM INSAN ALI
Read-only validator. Does not modify input files.
"""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path
from typing import Any
DEFAULT_SCHEMA = (
    Path(__file__).resolve().parent
    / "posture_archive_preflight.schema.json"
)
def load_json(path: Path) -> Any:
    """Load a JSON document without modifying it."""
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)
def validate_result(
    result_path: str | Path,
    schema_path: str | Path = DEFAULT_SCHEMA,
) -> dict[str, Any]:
    """Validate a preflight result against its JSON Schema."""
    result_file = Path(result_path)
    schema_file = Path(schema_path)
    try:
        result = load_json(result_file)
    except (OSError, UnicodeError, json.JSONDecodeError):
        return {
            "project": "Tamanna AI",
            "owner": "HM INSAN ALI",
            "status": "REVIEW_REQUIRED",
            "validation": "ERROR",
            "findings": ["RESULT_FILE_UNREADABLE_OR_INVALID_JSON"],
            "read_only": True,
        }
    try:
        schema = load_json(schema_file)
    except (OSError, UnicodeError, json.JSONDecodeError):
        return {
            "project": "Tamanna AI",
            "owner": "HM INSAN ALI",
            "status": "REVIEW_REQUIRED",
            "validation": "ERROR",
            "findings": ["SCHEMA_UNREADABLE_OR_INVALID_JSON"],
            "read_only": True,
        }
    try:
        from jsonschema import Draft202012Validator
    except ImportError:
        return {
            "project": "Tamanna AI",
            "owner": "HM INSAN ALI",
            "status": "REVIEW_REQUIRED",
            "validation": "ERROR",
            "findings": ["DEPENDENCY_MISSING: install jsonschema"],
            "read_only": True,
        }
    try:
        Draft202012Validator.check_schema(schema)
        validator = Draft202012Validator(schema)
        errors = sorted(
            validator.iter_errors(result),
            key=lambda error: list(map(str, error.absolute_path)),
        )
    except Exception:
        return {
            "project": "Tamanna AI",
            "owner": "HM INSAN ALI",
            "status": "REVIEW_REQUIRED",
            "validation": "ERROR",
            "findings": ["SCHEMA_VALIDATION_COULD_NOT_RUN"],
            "read_only": True,
        }
    findings = [
        f"{'/'.join(map(str, error.absolute_path)) or '$'}: {error.message}"
        for error in errors
    ]
    return {
        "project": "Tamanna AI",
        "owner": "HM INSAN ALI",
        "status": "PASS" if not findings else "REVIEW_REQUIRED",
        "validation": "VALID" if not findings else "INVALID",
        "findings": findings,
        "read_only": True,
    }
def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate a Tamanna AI preflight JSON result."
    )
    parser.add_argument(
        "--result",
        required=True,
        help="Path to a saved preflight result JSON file",
    )
    parser.add_argument(
        "--schema",
        default=str(DEFAULT_SCHEMA),
        help="Path to the preflight JSON Schema",
    )
    args = parser.parse_args()
    result = validate_result(args.result, args.schema)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result["validation"] == "VALID" else 1
if __name__ == "__main__":
    sys.exit(main())