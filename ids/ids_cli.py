File: ids/ids_cli.py

"""
Tamanna AI IDS Command-Line Interface.
Project: Tamanna AI
Owner: HM INSAN ALI
Commands:
    config  - Validate IDS configuration
    health  - Check IDS component health
    report  - Display IDS status report
This CLI does not modify operating-system firewall rules.
"""
from __future__ import annotations
import argparse
import json
import sys
from typing import Any
from ids.config_loader import IDSConfigError, load_config
from ids.health_check import run_health_check
from ids.ids_manager import IDSManager
from ids.ids_report import generate_report
def print_json(data: dict[str, Any]) -> None:
    """Print a dictionary as formatted JSON."""
    print(json.dumps(data, indent=2, ensure_ascii=False))
def command_config() -> int:
    """Validate and display the IDS configuration."""
    try:
        config = load_config()
    except IDSConfigError as exc:
        print(f"Configuration error: {exc}", file=sys.stderr)
        return 1
    print_json({
        "project": config.get("project"),
        "mode": config.get("mode"),
        "enabled": config.get("enabled", False),
        "automatic_ip_blocking": False,
        "modify_system_firewall": False,
        "configuration_valid": True,
    })
    return 0
def command_health() -> int:
    """Display IDS health information."""
    try:
        report = run_health_check(IDSManager())
    except Exception as exc:
        print(f"Health check failed: {exc}", file=sys.stderr)
        return 1
    print_json(report)
    return 0 if report.get("status") == "healthy" else 1
def command_report() -> int:
    """Display the current IDS report."""
    try:
        report = generate_report(IDSManager())
    except Exception as exc:
        print(f"Report generation failed: {exc}", file=sys.stderr)
        return 1
    print_json(report)
    return 0 if report.get("health_status") == "healthy" else 1
def main(argv: list[str] | None = None) -> int:
    """Parse arguments and run the requested command."""
    parser = argparse.ArgumentParser(
        prog="tamanna-ids",
        description="Tamanna AI IDS read-only monitoring CLI",
    )
    parser.add_argument(
        "command",
        choices=("config", "health", "report"),
        help="Operation to perform",
    )
    args = parser.parse_args(argv)
    commands = {
        "config": command_config,
        "health": command_health,
        "report": command_report,
    }
    return commands[args.command]()
if __name__ == "__main__":
    raise SystemExit(main())