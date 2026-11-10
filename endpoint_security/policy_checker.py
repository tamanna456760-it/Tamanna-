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


def _policy_violations(config: Any) -> list[str]:
    """Return policy violations found in an already-loaded configuration."""
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
        for option in (
            "kill_processes",
            "quarantine_files",
            "delete_files",
            "modify_system_settings",
        ):
            if enforcement.get(option) is not False:
                problems.append(f"enforcement.{option} must be false.")
        if enforcement.get("require_manual_approval") is not True:
            problems.append("enforcement.require_manual_approval must be true.")
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
            problems.append("process_monitoring.collect_command_line must be false.")
        if process_config.get("collect_environment_variables") is not False:
            problems.append("process_monitoring.collect_environment_variables must be false.")
    return problems


def check_policy(config_or_path: Any) -> dict[str, Any]:
    """Validate a config mapping or JSON file and return a stable report."""
    source = "in_memory"
    if isinstance(config_or_path, (str, Path)):
        path = Path(config_or_path)
        source = str(path)
        try:
            with path.open("r", encoding="utf-8") as handle:
                config = json.load(handle)
        except OSError as exc:
            return {
                "valid": False,
                "source": source,
                "violations": [f"Cannot read configuration ({exc.__class__.__name__})."],
            }
        except json.JSONDecodeError as exc:
            return {
                "valid": False,
                "source": source,
                "violations": [f"Invalid JSON at line {exc.lineno}, column {exc.colno}."],
            }
    else:
        config = config_or_path
    violations = _policy_violations(config)
    return {
        "valid": not violations,
        "source": source,
        "violations": violations,
        "mode": config.get("mode") if isinstance(config, dict) else None,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check Tamanna AI Endpoint Security policy defaults."
    )
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    args = parser.parse_args()
    report = check_policy(args.config)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report["valid"] else 1


if __name__ == "__main__":
    sys.exit(main())
