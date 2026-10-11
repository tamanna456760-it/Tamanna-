
"""
Tamanna AI Advanced Firewall Manager
Owner: HM INSAN ALI

Safe-by-default security manager.
This module validates configuration and reports status.
It does not modify operating-system firewall rules.
"""

from __future__ import annotations

import ipaddress
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


BASE_DIR = Path(__file__).resolve().parent
CONFIG_FILE = BASE_DIR / "firewall_config.json"
AUDIT_FILE = BASE_DIR / "firewall_audit.jsonl"

SUPPORTED_MODES = {"audit_only", "monitor", "enforce"}


class FirewallConfigError(ValueError):
    """Raised when firewall configuration is invalid."""


def load_config() -> dict[str, Any]:
    """Load and validate the firewall configuration."""
    if not CONFIG_FILE.is_file():
        raise FirewallConfigError(
            f"Configuration file not found: {CONFIG_FILE.name}"
        )

    try:
        with CONFIG_FILE.open("r", encoding="utf-8") as file:
            config = json.load(file)
    except (OSError, json.JSONDecodeError) as exc:
        raise FirewallConfigError(
            "Unable to read valid firewall_config.json"
        ) from exc

    validate_config(config)
    return config


def validate_config(config: dict[str, Any]) -> None:
    """Reject unsafe or malformed configuration values."""
    if not isinstance(config, dict):
        raise FirewallConfigError("Configuration must be a JSON object.")

    mode = config.get("mode")
    if mode not in SUPPORTED_MODES:
        raise FirewallConfigError("Unsupported firewall mode.")

    policy = config.get("security_policy", {})
    if not isinstance(policy, dict):
        raise FirewallConfigError("security_policy must be an object.")

    if policy.get("default_policy") != "deny":
        raise FirewallConfigError("Default policy must be deny.")

    network = config.get("network_protection", {})
    if not isinstance(network, dict):
        raise FirewallConfigError(
            "network_protection must be an object."
        )

    for field in ("allowed_ips", "blocked_ips"):
        addresses = network.get(field, [])
        if not isinstance(addresses, list):
            raise FirewallConfigError(f"{field} must be a list.")

        for address in addresses:
            if not isinstance(address, str):
                raise FirewallConfigError(
                    f"{field} entries must be strings."
                )
            try:
                ipaddress.ip_address(address)
            except ValueError as exc:
                raise FirewallConfigError(
                    f"Invalid IP address in {field}."
                ) from exc

    ports = network.get("allowed_ports", [])
    if not isinstance(ports, list):
        raise FirewallConfigError("allowed_ports must be a list.")

    for port in ports:
        if type(port) is not int or not 1 <= port <= 65535:
            raise FirewallConfigError(
                "Each allowed port must be an integer from 1 to 65535."
            )

    # Real OS firewall enforcement is deliberately not implemented here.
    system_firewall = config.get("system_firewall", {})
    if not isinstance(system_firewall, dict):
        raise FirewallConfigError("system_firewall must be an object.")


def record_event(event: str, details: dict[str, Any] | None = None) -> None:
    """Append a security event without storing secrets."""
    safe_details = details if isinstance(details, dict) else {}

    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event": str(event)[:120],
        "details": safe_details,
    }

    try:
        with AUDIT_FILE.open("a", encoding="utf-8") as file:
            file.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except OSError:
        # Do not silently claim that the audit event was saved.
        raise RuntimeError("Unable to write the firewall audit log.")


def get_status() -> dict[str, Any]:
    """Return a safe status summary."""
    config = load_config()
    network = config.get("network_protection", {})
    audit = config.get("audit", {})

    return {
        "name": config.get("name", "Tamanna AI Firewall"),
        "version": config.get("version", "unknown"),
        "enabled": config.get("enabled", False),
        "mode": config["mode"],
        "default_policy": config["security_policy"]["default_policy"],
        "allowed_ip_count": len(network.get("allowed_ips", [])),
        "allowed_port_count": len(network.get("allowed_ports", [])),
        "audit_enabled": audit.get("enabled", False),
        "system_firewall_integration": "not_implemented",
        "system_rules_modified": False,
        "configuration_valid": True,
    }


def run_health_check() -> dict[str, Any]:
    """Validate the config and record a health-check event."""
    status = get_status()
    record_event(
        "firewall_health_check",
        {
            "mode": status["mode"],
            "configuration_valid": status["configuration_valid"],
        },
    )
    return status


if __name__ == "__main__":
    try:
        result = run_health_check()
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except (FirewallConfigError, RuntimeError) as exc:
        print(json.dumps({
            "ok": False,
            "error": str(exc),
        }, indent=2, ensure_ascii=False))
        raise SystemExit(1)
