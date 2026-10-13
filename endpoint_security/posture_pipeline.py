#!/usr/bin/env python3
"""Tamanna AI read-only security posture report pipeline.
Owner: HM INSAN ALI
Loads check results, builds a unified posture report, validates its schema,
and writes the output without overwriting an existing file.
"""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path
from endpoint_security.unified_posture_report import load_checks, build_posture_report
from endpoint_security.posture_schema_validator import validate_posture_report
def run_pipeline(input_path: Path, output_path: Path, schema_path: Path) -> dict:
    if not input_path.is_file():
        raise FileNotFoundError(f"Input checks file not found: {input_path}")
    if not schema_path.is_file():
        raise FileNotFoundError(f"Schema file not found: {schema_path}")
    checks = load_checks(input_path)
    report = build_posture_report(checks)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    # Exclusive creation prevents accidental overwriting of an existing report.
    with output_path.open("x", encoding="utf-8") as file:
        json.dump(report, file, indent=2, ensure_ascii=False)
        file.write("\n")
    validation = validate_posture_report(output_path, schema_path)
    return {
        "project": "Tamanna AI",
        "owner": "HM INSAN ALI",
        "report_path": str(output_path),
        "report_status": report.get("status", "UNKNOWN"),
        "schema_validation": validation.get("status", "UNKNOWN"),
        "read_only": True,
    }
def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build and validate a Tamanna AI security posture report."
    )
    parser.add_argument("--input", required=True, type=Path,
                        help="JSON file containing an array of check objects.")
    parser.add_argument("--output", required=True, type=Path,
                        help="New report path; existing files are never overwritten.")
    parser.add_argument(
        "--schema",
        type=Path,
        default=Path(__file__).resolve().parent / "security_posture_schema.json",
        help="JSON Schema path.",
    )
    args = parser.parse_args()
    try:
        result = run_pipeline(args.input, args.output, args.schema)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        if result["schema_validation"] != "VALID":
            return 1
        if result["report_status"] != "VALID":
            return 1
        return 0
    except FileExistsError:
        print("ERROR: Output already exists; choose a new output path.",
              file=sys.stderr)
        return 2
    except (OSError, ValueError, TypeError, json.JSONDecodeError) as exc:
        print(f"ERROR: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2
if __name__ == "__main__":
    sys.exit(main())