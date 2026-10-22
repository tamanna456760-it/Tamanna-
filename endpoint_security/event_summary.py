#!/usr/bin/env python3
"""Summarize Tamanna AI Endpoint Security JSONL events.
Owner: HM INSAN ALI
Read-only reporting tool. It never changes or deletes the source log.
"""
from __future__ import annotations
import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any
DEFAULT_LOG = Path("data/endpoint_security_events.jsonl")
def summarize_events(log_path: Path) -> dict[str, Any]:
    total = 0
    malformed = 0
    event_types: Counter[str] = Counter()
    severities: Counter[str] = Counter()
    with log_path.open("r", encoding="utf-8") as log_file:
        for line in log_file:
            if not line.strip():
                continue
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                malformed += 1
                continue
            if not isinstance(event, dict):
                malformed += 1
                continue
            total += 1
            event_type = event.get("event_type", event.get("type", "unknown"))
            severity = event.get("severity", "unknown")
            if not isinstance(event_type, str):
                event_type = "invalid"
            if not isinstance(severity, str):
                severity = "invalid"
            event_types[event_type] += 1
            severities[severity.lower()] += 1
    return {
        "project": "Tamanna AI",
        "owner": "HM INSAN ALI",
        "component": "Endpoint Security",
        "report_type": "event_summary",
        "valid_events": total,
        "malformed_lines": malformed,
        "event_types": dict(event_types.most_common()),
        "severities": dict(severities.most_common()),
    }
def main() -> int:
    parser = argparse.ArgumentParser(
        description="Summarize a Tamanna AI Endpoint Security event log."
    )
    parser.add_argument(
        "--log",
        type=Path,
        default=DEFAULT_LOG,
        help="Path to the JSONL event log.",
    )
    args = parser.parse_args()
    try:
        summary = summarize_events(args.log)
    except OSError as exc:
        print(f"ERROR: Cannot read log ({exc.__class__.__name__}).")
        return 2
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 1 if summary["malformed_lines"] else 0
if __name__ == "__main__":
    sys.exit(main())