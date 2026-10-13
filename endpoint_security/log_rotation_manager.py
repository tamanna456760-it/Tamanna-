#!/usr/bin/env python3
"""Read-only log rotation status checker for Tamanna AI.
Owner: HM INSAN ALI
This module never renames, truncates, or deletes log files.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
DEFAULT_MAX_BYTES = 5 * 1024 * 1024  # 5 MiB
def get_rotation_status(
    log_path: Path,
    max_bytes: int = DEFAULT_MAX_BYTES,
) -> dict:
    """Report whether a log file has reached its size threshold."""
    if max_bytes <= 0:
        return {
            "valid": False,
            "status": "INVALID_THRESHOLD",
            "message": "max_bytes must be greater than zero.",
        }
    if not log_path.exists():
        return {
            "valid": True,
            "status": "MISSING",
            "path": str(log_path),
            "size_bytes": None,
            "max_bytes": max_bytes,
            "rotation_needed": False,
            "message": "Log file does not exist yet.",
        }
    try:
        if not log_path.is_file():
            return {
                "valid": False,
                "status": "INVALID_PATH",
                "path": str(log_path),
                "message": "Log path is not a regular file.",
            }
        size_bytes = log_path.stat().st_size
    except OSError as exc:
        return {
            "valid": False,
            "status": "ERROR",
            "path": str(log_path),
            "message": f"{type(exc).__name__}: {exc}",
        }
    rotation_needed = size_bytes >= max_bytes
    return {
        "valid": True,
        "project": "Tamanna AI",
        "owner": "HM INSAN ALI",
        "path": str(log_path),
        "status": "ROTATION_RECOMMENDED" if rotation_needed else "OK",
        "size_bytes": size_bytes,
        "max_bytes": max_bytes,
        "rotation_needed": rotation_needed,
        "action_taken": False,
        "message": (
            "Log has reached the configured size threshold."
            if rotation_needed
            else "Log is below the configured size threshold."
        ),
    }
def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check Tamanna AI event log rotation status."
    )
    parser.add_argument(
        "--log",
        type=Path,
        default=Path("data/endpoint_security_events.jsonl"),
        help="Path to the event log.",
    )
    parser.add_argument(
        "--max-bytes",
        type=int,
        default=DEFAULT_MAX_BYTES,
        help="Size threshold in bytes; default is 5 MiB.",
    )
    args = parser.parse_args()
    result = get_rotation_status(args.log, args.max_bytes)
    print(json.dumps(result, indent=2))
    return 0 if result.get("valid") else 1
if __name__ == "__main__":
    raise SystemExit(main())