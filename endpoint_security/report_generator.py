#!/usr/bin/env python3
"""Generate a read-only Tamanna AI Endpoint Security report.
Owner: HM INSAN ALI
The report contains configuration validation results only.
It does not claim that the host is malware-free.
"""
from __future__ import annotations
import argparse
import json
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from endpoint_security.config_validator import validate_config
DEFAULT_CONFIG = Path("endpoint_security/endpoint_config.json")
def build_report(config_path: Path) -> dict[str, Any]:
    """Build a security report without modifying the configuration."""
    report: dict[str, Any] = {
        "project": "Tamanna AI",
        "owner": "HM INSAN ALI",
        "component": "Endpoint Security",
        "report_type": "configuration_audit",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "platform": platform.system(),
        "mode": "monitor_only",
        "configuration_file": config_path.name,
        "configuration_valid": False,
        "errors": [],
        "limitations": [
            "This report does not prove the host is malware-free.",
            "It does not perform a full malware scan.",
            "It does not confirm continuous monitoring is running.",
            "It does not enable enforcement actions.",
        ],
    }
    try:
        with config_path.open("r", encoding="utf-8") as config_file:
            config = json.load(config_file)
    except OSError as exc:
        report["errors"] = [
            f"Cannot read configuration ({exc.__class__.__name__})."
        ]
        return report
    except json.JSONDecodeError as exc:
        report["errors"] = [
            f"Invalid JSON at line {exc.lineno}, column {exc.colno}."
        ]
        return report
    errors = validate_config(config)
    report["configuration_valid"] = not errors
    report["errors"] = errors
    if isinstance(config, dict):
        report["configured_enabled"] = config.get("enabled") is True
        report["configured_mode"] = config.get("mode", "unknown")
        enforcement = config.get("enforcement", {})
        if isinstance(enforcement, dict):
            report["destructive_actions_enabled"] = any(
                enforcement.get(option) is True
                for option in (
                    "kill_processes",
                    "quarantine_files",
                    "delete_files",
                    "modify_system_settings",
                )
            )
        else:
            report["destructive_actions_enabled"] = "unknown"
    report["status"] = (
        "PASS" if report["configuration_valid"] else "FAIL"
    )
    return report
def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate a Tamanna AI Endpoint Security JSON report."
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_CONFIG,
        help="Path to the Endpoint Security configuration.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Optional output path for the JSON report.",
    )
    args = parser.parse_args()
    report = build_report(args.config)
    rendered = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    if args.output:
        try:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            with args.output.open("x", encoding="utf-8") as output_file:
                output_file.write(rendered)
        except FileExistsError:
            print("ERROR: Output file already exists; refusing to overwrite.")
            return 2
        except OSError as exc:
            print(f"ERROR: Cannot write report ({exc.__class__.__name__}).")
            return 2
    else:
        print(rendered, end="")
    return 0 if report.get("configuration_valid") else 1
if __name__ == "__main__":
    sys.exit(main())