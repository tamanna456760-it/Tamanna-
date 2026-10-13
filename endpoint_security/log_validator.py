#!/usr/bin/env python3
"""Validate Tamanna AI Endpoint Security JSONL event logs.
Owner: HM INSAN ALI
Read-only validator:
- Does not modify or delete log files.
- Checks each non-empty line for valid JSON.
- Reports malformed lines without printing their contents.
"""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path
from typing import Any
def validate_jsonl(path: Path) -> tuple[int, list[int]]:
    """Return (valid_line_count, malformed_line_numbers)."""
    valid_count = 0
    malformed_lines: list[int] = []
    try:
        with path.open("r", encoding="utf-8") as log_file:
            for line_number, line in enumerate(log_file, start=1):
                if not line.strip():
                    continue
                try:
                    value: Any = json.loads(line)
                except json.JSONDecodeError:
                    malformed_lines.append(line_number)
                    continue
                if not isinstance(value, dict):
                    malformed_lines.append(line_number)
                    continue
                valid_count += 1
    except OSError as exc:
        raise RuntimeError(
            f"Cannot read log file ({exc.__class__.__name__})."
        ) from exc
    return valid_count, malformed_lines
def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate a Tamanna AI Endpoint Security JSONL log."
    )
    parser.add_argument(
        "log_file",
        type=Path,
        help="Path to the JSONL event log to validate.",
    )
    args = parser.parse_args()
    if not args.log_file.is_file():
        print("ERROR: Log file does not exist or is not a regular file.")
        return 2
    try:
        valid_count, malformed_lines = validate_jsonl(args.log_file)
    except RuntimeError as exc:
        print(f"ERROR: {exc}")
        return 2
    print(f"Valid event records: {valid_count}")
    print(f"Malformed records: {len(malformed_lines)}")
    if malformed_lines:
        print("Malformed line numbers: " + ", ".join(map(str, malformed_lines)))
        return 1
    print("PASS: All non-empty lines contain JSON objects.")
    return 0
if __name__ == "__main__":
    sys.exit(main())