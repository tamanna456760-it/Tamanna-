#!/usr/bin/env python3
"""Read-only security configuration drift detector.
Owner: HM INSAN ALI
Detects changes from expected Endpoint Security defaults.
Does not modify configuration.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from typing import Any
DEFAULT_CONFIG = (
    Path(__file__).resolve().parent / "endpoint_config.json"
)
EXPECTED_VALUES = {
    "enabled": True,
    "mode": "monitor_only",
    "process_monitoring.collect_command_line": False,
    "process_monitoring.collect_environment_variables": False,
    "logging.enabled": True,
    "logging.redact_secrets": True,
    "enforcement.kill_processes": False,
    "enforcement.quarantine_files": False,
    "enforcement.delete_files": False,
    "enforcement.modify_system_settings": False,
    "enforcement.require_manual_approval": True,
}
def get_nested_value(data: dict, dotted_key: str) -> tuple[bool, Any]:
    """Return (found, value) for a dotted configuration key."""
    current: Any = data
    for key in dotted_key.split("."):
        if not isinstance(current, dict) or key not in current:
            return False, None
        current = current[key]
    return True, current
def detect_config_drift(config_path: Path) -> dict:
    """Compare configured values with expected security defaults."""
    try:
        with config_path.open("r", encoding="utf-8") as handle:
            config = json.load(handle)
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        return {
            "valid": False,
            "status": "ERROR",
            "config_path": str(config_path),
            "errors": [f"{type(exc).__name__}: {exc}"],
            "drift": [],
        }
    if not isinstance(config, dict):
        return {
            "valid": False,
            "status": "ERROR",
            "config_path": str(config_path),
            "errors": ["Configuration root must be a JSON object."],
            "drift": [],
        }
    drift = []
    for key, expected in EXPECTED_VALUES.items():
        found, actual = get_nested_value(config, key)
        if not found:
            drift.append({
                "setting": key,
                "status": "MISSING",
                "expected": expected,
            })
        elif actual != expected or type(actual) is not type(expected):
            drift.append({
                "setting": key,
                "status": "CHANGED",
                "expected": expected,
                "actual": actual,
            })
    return {
        "valid": True,
        "project": "Tamanna AI",
        "owner": "HM INSAN ALI",
        "config_path": str(config_path),
        "status": "DRIFT_DETECTED" if drift else "NO_DRIFT",
        "drift_count": len(drift),
        "drift": drift,
        "read_only": True,
        "note": (
            "Comparison against built-in expected values only. "
            "No settings were changed."
        ),
    }
def main() -> int:
    parser = argparse.ArgumentParser(
        description="Detect Tamanna AI security configuration drift."
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_CONFIG,
        help="Path to endpoint_config.json.",
    )
    args = parser.parse_args()
    result = detect_config_drift(args.config)
    print(json.dumps(result, indent=2))
    if not result.get("valid"):
        return 2
    return 1 if result["status"] == "DRIFT_DETECTED" else 0
if __name__ == "__main__":
    raise SystemExit(main())