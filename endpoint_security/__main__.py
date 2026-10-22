"""Command-line interface for Tamanna AI Endpoint Security.
Owner: HM INSAN ALI
All commands are read-only and run in monitor-only mode.
"""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path
from .health_check import run_health_check
from .manager import EndpointSecurityManager
DEFAULT_CONFIG = "endpoint_security/endpoint_config.json"
def load_config(config_path: str) -> dict:
    """Load and validate the configuration file."""
    with Path(config_path).open("r", encoding="utf-8") as file_handle:
        config = json.load(file_handle)
    if not isinstance(config, dict):
        raise ValueError("Configuration root must be a JSON object")
    return config
def print_json(result: dict) -> None:
    """Print a structured result."""
    print(json.dumps(result, indent=2, ensure_ascii=False))
def main() -> int:
    parser = argparse.ArgumentParser(
        description="Tamanna AI Endpoint Security CLI"
    )
    parser.add_argument(
        "--config",
        default=DEFAULT_CONFIG,
        help="Path to endpoint security configuration JSON",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("health", help="Check configuration health")
    subparsers.add_parser("processes", help="Inspect running processes")
    file_parser = subparsers.add_parser(
        "file-hash",
        help="Calculate SHA-256 for one selected file",
    )
    file_parser.add_argument("path", help="File path to inspect")
    args = parser.parse_args()
    if args.command == "health":
        result = run_health_check(args.config)
        print_json(result)
        return 0 if result.get("status") in {"healthy", "disabled"} else 1
    try:
        config = load_config(args.config)
        manager = EndpointSecurityManager(config)
        if args.command == "processes":
            result = manager.scan_processes()
        elif args.command == "file-hash":
            result = manager.check_file(args.path)
        else:
            parser.error("Unsupported command")
            return 2
        print_json(result)
        return 0 if result.get("status") in {
            "ok", "disabled", "unavailable"
        } else 1
    except (OSError, ValueError, TypeError, json.JSONDecodeError) as exc:
        print_json({
            "status": "error",
            "component": "Endpoint Security",
            "error": str(exc),
        })
        return 1
if __name__ == "__main__":
    raise SystemExit(main())