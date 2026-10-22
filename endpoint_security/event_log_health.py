#!/usr/bin/env python3
"""Read-only health check for Tamanna AI security event logs.
Owner: HM INSAN ALI
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from endpoint_security.event_schema_validator import validate_event_log
from endpoint_security.log_validator import validate_log
def check_event_log(log_path: Path) -> dict:
    """Check log existence, JSONL structure, and event schema."""
    if not log_path.exists():
        return {
            "project": "Tamanna AI",
            "owner": "HM INSAN ALI",
            "status": "MISSING",
            "path": str(log_path),
            "message": "Event log file does not exist yet.",
        }
    if not log_path.is_file():
        return {
            "project": "Tamanna AI",
            "owner": "HM INSAN ALI",
            "status": "ERROR",
            "path": str(log_path),
            "message": "Log path is not a regular file.",
        }
    try:
        jsonl_result = validate_log(log_path)
        schema_result = validate_event_log(log_path)
    except (OSError, UnicodeError, ValueError, TypeError) as exc:
        return {
            "project": "Tamanna AI",
            "owner": "HM INSAN ALI",
            "status": "ERROR",
            "path": str(log_path),
            "message": f"{type(exc).__name__}: {exc}",
        }
    jsonl_valid = bool(
        jsonl_result.get("valid", jsonl_result.get("healthy", False))
    )
    schema_valid = bool(
        schema_result.get("valid", schema_result.get("healthy", False))
    )
    return {
        "project": "Tamanna AI",
        "owner": "HM INSAN ALI",
        "path": str(log_path),
        "status": "PASS" if jsonl_valid and schema_valid else "FAIL",
        "jsonl_validation": jsonl_result,
        "schema_validation": schema_result,
        "note": (
            "Read-only structural check. It does not prove that events "
            "are complete, authentic, or free of tampering."
        ),
    }
def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check Tamanna AI endpoint security event logs."
    )
    parser.add_argument(
        "--log",
        type=Path,
        default=Path("data/endpoint_security_events.jsonl"),
        help="Path to the JSONL event log.",
    )
    args = parser.parse_args()
    result = check_event_log(args.log)
    print(json.dumps(result, indent=2))
    return 0 if result.get("status") == "PASS" else 1
if __name__ == "__main__":
    raise SystemExit(main())