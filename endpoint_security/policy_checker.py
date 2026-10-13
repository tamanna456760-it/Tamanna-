#!/usr/bin/env python3
"""Read-only security policy checker for Tamanna AI.
Owner: HM INSAN ALI
Checks selected security defaults without changing configuration.
"""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path
from typing import Any
DEFAULT_CONFIG = Path("endpoint_security/endpoint_config.json")
def check_policy(config: Any) -> list[str]:
    """Return policy violations found in the configuration."""
    problems: list[str] = []
    if not isinstance(config, dict):
        return ["Configuration root must be a JSON object."]
    if config.get("mode") != "monitor_only":
        problems.append("mode must remain monitor_only.")
    if config.get("enabled") is not True:
        problems.append("Endpoint Security must be enabled.")
    enforcement = config.get("enforcement")
    if not isinstance(enforcement, dict):
        problems.append("enforcement must be a JSON object.")
    else:
        protected_options = (
            "kill_processes",
            "quarantine_files",
            "delete_files",
            "modify_system_settings",
        )
        for option in protected_options:
            if enforcement.get(option) is not False:
                problems.append(f"enforcement.{option} must be false.")
        if enforcement.get("require_manual_approval") is not True:
            problems.append(
                "enforcement.require_manual_approval must be true."
            )
    logging_config = config.get("logging")
    if not isinstance(logging_config, dict):
        problems.append("logging must be a JSON object.")
    else:
        if logging_config.get("enabled") is not True:
            problems.append("logging.enabled must be true.")
        if logging_config.get("redact_secrets") is not True:
            problems.append("logging.redact_secrets must be true.")
    process_config = config.get("process_monitoring")
    if not isinstance(process_config, dict):
        problems.append("process_monitoring must be a JSON object.")
    else:
        if process_config.get("collect_command_line") is not False:
            problems.append(
                "process_monitoring.collect_command_line must be false."
            )
        if process_config.get("collect_environment_variables") is not False:
            problems.append(
                "process_monitoring.collect_environment_variables must be false."
            )
    return problems
def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check Tamanna AI Endpoint Security policy defaults."
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_CONFIG,
        help="Configuration JSON path.",
    )
    args = parser.parse_args()
    try:
        with args.config.open("r", encoding="utf-8") as file:
            config = json.load(file)
    except OSError as exc:
        print(f"ERROR: Cannot read configuration ({exc.__class__.__name__}).")
        return 2
    except json.JSONDecodeError as exc:
        print(f"ERROR: Invalid JSON at line {exc.lineno}, column {exc.colno}.")
        return 2
    problems = check_policy(config)
    if problems:
        print("POLICY CHECK: FAIL")
        for problem in problems:
            print(f"- {problem}")
        return 1
    print("POLICY CHECK: PASS")
    print("Mode: monitor_only")
    print("Destructive enforcement: disabled")
    print("Sensitive process details collection: disabled")
    return 0
if __name__ == "__main__":
    sys.exit(main())