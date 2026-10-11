"""
Tamanna AI — Security Policy Validator
Owner: HM INSAN ALI
Validates firewall configuration before it is used.
This module does not change operating-system firewall rules.
"""
from __future__ import annotations
import ipaddress
import json
from pathlib import Path
from typing import Any
DEFAULT_CONFIG_PATH = Path(__file__).with_name("firewall_config.json")
VALID_MODES = {"audit_only", "monitor", "enforce"}
def _error(code: str, message: str, field: str) -> dict[str, str]:
    return {
        "code": code,
        "message": message,
        "field": field,
    }
def validate_policy(
    config: Any,
) -> dict[str, Any]:
    """
    Validate a loaded policy dictionary.
    Returns:
        {
            "valid": bool,
            "errors": [...],
            "warnings": [...]
        }
    """
    errors: list[dict[str, str]] = []
    warnings: list[dict[str, str]] = []
    if not isinstance(config, dict):
        return {
            "valid": False,
            "errors": [
                _error(
                    "invalid_root",
                    "Configuration root must be a JSON object.",
                    "$",
                )
            ],
            "warnings": [],
        }
    mode = config.get("mode", "audit_only")
    if mode not in VALID_MODES:
        errors.append(
            _error(
                "invalid_mode",
                "Mode must be audit_only, monitor, or enforce.",
                "mode",
            )
        )
    default_policy = config.get("default_policy", "deny")
    if default_policy not in {"deny", "allow"}:
        errors.append(
            _error(
                "invalid_default_policy",
                "default_policy must be deny or allow.",
                "default_policy",
            )
        )
    elif default_policy == "allow":
        warnings.append(
            _error(
                "permissive_default",
                "Default allow can expose services unintentionally.",
                "default_policy",
            )
        )
    if not isinstance(config.get("default_deny", True), bool):
        errors.append(
            _error(
                "invalid_boolean",
                "default_deny must be a boolean.",
                "default_deny",
            )
        )
    allowed_ips = config.get("allowed_ips", [])
    if not isinstance(allowed_ips, list):
        errors.append(
            _error(
                "invalid_list",
                "allowed_ips must be a list of IP addresses.",
                "allowed_ips",
            )
        )
    else:
        for index, value in enumerate(allowed_ips):
            try:
                ipaddress.ip_address(value)
            except (ValueError, TypeError):
                errors.append(
                    _error(
                        "invalid_ip",
                        "Entry must be a valid IPv4 or IPv6 address.",
                        f"allowed_ips[{index}]",
                    )
                )
    blocked_ips = config.get("blocked_ips", [])
    if not isinstance(blocked_ips, list):
        errors.append(
            _error(
                "invalid_list",
                "blocked_ips must be a list of IP addresses.",
                "blocked_ips",
            )
        )
    else:
        for index, value in enumerate(blocked_ips):
            try:
                ipaddress.ip_address(value)
            except (ValueError, TypeError):
                errors.append(
                    _error(
                        "invalid_ip",
                        "Entry must be a valid IPv4 or IPv6 address.",
                        f"blocked_ips[{index}]",
                    )
                )
    allowed_ports = config.get("allowed_ports", [])
    if not isinstance(allowed_ports, list):
        errors.append(
            _error(
                "invalid_list",
                "allowed_ports must be a list of port numbers.",
                "allowed_ports",
            )
        )
    else:
        for index, port in enumerate(allowed_ports):
            if (
                isinstance(port, bool)
                or not isinstance(port, int)
                or not 1 <= port <= 65535
            ):
                errors.append(
                    _error(
                        "invalid_port",
                        "Port must be an integer between 1 and 65535.",
                        f"allowed_ports[{index}]",
                    )
                )
    api_protection = config.get("api_protection", {})
    if not isinstance(api_protection, dict):
        errors.append(
            _error(
                "invalid_section",
                "api_protection must be a JSON object.",
                "api_protection",
            )
        )
    else:
        max_body = api_protection.get("max_body_bytes", 1048576)
        if (
            isinstance(max_body, bool)
            or not isinstance(max_body, int)
            or max_body < 1
        ):
            errors.append(
                _error(
                    "invalid_size_limit",
                    "max_body_bytes must be a positive integer.",
                    "api_protection.max_body_bytes",
                )
            )
    rate_limits = config.get("rate_limits", {})
    if not isinstance(rate_limits, dict):
        errors.append(
            _error(
                "invalid_section",
                "rate_limits must be a JSON object.",
                "rate_limits",
            )
        )
    else:
        for key in ("requests_per_minute", "burst"):
            value = rate_limits.get(key)
            if value is not None and (
                isinstance(value, bool)
                or not isinstance(value, int)
                or value < 1
            ):
                errors.append(
                    _error(
                        "invalid_rate_limit",
                        f"{key} must be a positive integer.",
                        f"rate_limits.{key}",
                    )
                )
    system_firewall = config.get("system_firewall", {})
    if not isinstance(system_firewall, dict):
        errors.append(
            _error(
                "invalid_section",
                "system_firewall must be a JSON object.",
                "system_firewall",
            )
        )
    else:
        if system_firewall.get("modify_system_rules", False) is True:
            if system_firewall.get("explicit_approval_required", True) is True:
                warnings.append(
                    _error(
                        "approval_required",
                        "System firewall changes require explicit approval.",
                        "system_firewall",
                    )
                )
            else:
                errors.append(
                    _error(
                        "unsafe_firewall_change",
                        "System firewall changes cannot be enabled without an approval gate.",
                        "system_firewall.modify_system_rules",
                    )
                )
    if mode == "enforce":
        warnings.append(
            _error(
                "enforcement_not_verified",
                "Enforce mode requires a separately tested enforcement integration.",
                "mode",
            )
        )
    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
    }
def load_and_validate_policy(
    path: str | Path = DEFAULT_CONFIG_PATH,
) -> dict[str, Any]:
    """Load JSON safely and validate it without modifying the file."""
    config_path = Path(path)
    try:
        with config_path.open("r", encoding="utf-8") as file:
            config = json.load(file)
    except FileNotFoundError:
        return {
            "valid": False,
            "errors": [
                _error(
                    "config_not_found",
                    "Configuration file was not found.",
                    str(config_path),
                )
            ],
            "warnings": [],
        }
    except (OSError, json.JSONDecodeError):
        return {
            "valid": False,
            "errors": [
                _error(
                    "config_read_error",
                    "Configuration file could not be read as valid JSON.",
                    str(config_path),
                )
            ],
            "warnings": [],
        }
    return validate_policy(config)
if __name__ == "__main__":
    result = load_and_validate_policy()
    print("Tamanna AI — Security Policy Validation")
    print("Valid:", result["valid"])
    print("Errors:", len(result["errors"]))
    print("Warnings:", len(result["warnings"]))
    for item in result["errors"]:
        print("ERROR:", item["code"], "-", item["field"])
    for item in result["warnings"]:
        print("WARNING:", item["code"], "-", item["field"])
    if not result["valid"]:
        raise SystemExit(1)