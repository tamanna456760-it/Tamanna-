#!/usr/bin/env python3
"""Validate Tamanna AI Endpoint Security configuration.
Owner: HM INSAN ALI
This validator is read-only. It does not change configuration or enforce
security actions on the host.
"""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path
from typing import Any
DEFAULT_CONFIG = Path("endpoint_security/endpoint_config.json")
ALLOWED_MODES = {"monitor_only"}
FORBIDDEN_ENFORCEMENT_OPTIONS = (
    "kill_processes",
    "quarantine_files",
    "delete_files",
    "modify_system_settings",
)
def validate_config(config: Any) -> list[str]:
    """Return configuration validation errors."""
    errors: list[str] = []
    if not isinstance(config, dict):
        return ["Configuration root must be a JSON object."]
    if config.get("project") != "Tamanna AI":
        errors.append("project must be 'Tamanna AI'.")
    if config.get("owner") != "HM INSAN ALI":
        errors.append("owner must be 'HM INSAN ALI'.")
    if config.get("mode") not in ALLOWED_MODES:
        errors.append("mode must be 'monitor_only'.")
    if config.get("enabled") is not True:
        errors.append("enabled must be true.")
    enforcement = config.get("enforcement")
    if not isinstance(enforcement, dict):
        errors.append("enforcement must be a JSON object.")
    else:
        for option in FORBIDDEN_ENFORCEMENT_OPTIONS:
            if enforcement.get(option) is True:
                errors.append(
                    f"enforcement.{option} must not be enabled."
                )
        if enforcement.get("require_manual_approval") is not True:
            errors.append(
                "enforcement.require_manual_approval must be true."
            )
    logging_config = config.get("logging")
    if not isinstance(logging_config, dict):
        errors.append("logging must be a JSON object.")
    else:
        if logging_config.get("enabled") is not True:
            errors.append("logging.enabled must be true.")
        if logging_config.get("redact_secrets") is not True:
            errors.append("logging.redact_secrets must be true.")
        max_event_size = logging_config.get("max_event_size_bytes")
        if (
            isinstance(max_event_size, bool)
            or not isinstance(max_event_size, int)
            or max_event_size <= 0
        ):
            errors.append(
                "logging.max_event_size_bytes must be a positive integer."
            )
    file_integrity = config.get("file_integrity")
    if not isinstance(file_integrity, dict):
        errors.append("file_integrity must be a JSON object.")
    else:
        if file_integrity.get("hash_algorithm") != "sha256":
            errors.append("file_integrity.hash_algorithm must be 'sha256'.")
        max_file_size = file_integrity.get("max_file_size_bytes")
        if (
            isinstance(max_file_size, bool)
            or not isinstance(max_file_size, int)
            or max_file_size <= 0
        ):
            errors.append(
                "file_integrity.max_file_size_bytes must be a positive integer."
            )
    return errors
def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate Tamanna AI Endpoint Security configuration."
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_CONFIG,
        help="Configuration JSON path.",
    )
    args = parser.parse_args()
    try:
        with args.config.open("r", encoding="utf-8") as config_file:
            config = json.load(config_file)
    except OSError as exc:
        print(f"ERROR: Cannot read configuration ({exc.__class__.__name__}).")
        return 2
    except json.JSONDecodeError as exc:
        print(f"ERROR: Invalid JSON at line {exc.lineno}, column {exc.colno}.")
        return 2
    errors = validate_config(config)
    if errors:
        print("FAIL: Endpoint Security configuration has errors:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("PASS: Endpoint Security configuration checks passed.")
    print("Mode: monitor_only")
    print("Enforcement: destructive actions must remain disabled.")
    return 0
if __name__ == "__main__":
    sys.exit(main())