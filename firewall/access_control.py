
"""
Tamanna AI — Advanced Access Control Engine
Owner: HM INSAN ALI

Validates IP addresses, ports, and access policies.
This module evaluates policy; it does not block network traffic.
"""

from __future__ import annotations

import ipaddress
from typing import Any


def _parse_ip(value: str):
    """Return a normalized IP object or None for invalid input."""
    if not isinstance(value, str):
        return None

    try:
        return ipaddress.ip_address(value.strip())
    except ValueError:
        return None


def is_allowed_ip(client_ip: str, config: dict[str, Any]) -> bool:
    """Check an IP against explicit allow/deny lists."""
    address = _parse_ip(client_ip)

    if address is None:
        return False

    network = config.get("network_protection", config)
    if not isinstance(network, dict):
        return False

    allowed = network.get("allowed_ips", [])
    blocked = network.get("blocked_ips", [])

    if not isinstance(allowed, list) or not isinstance(blocked, list):
        return False

    # Explicit deny takes precedence over allow.
    for item in blocked:
        denied = _parse_ip(item)
        if denied is not None and denied == address:
            return False

    # Loopback is only allowed when explicitly enabled.
    if address.is_loopback:
        return network.get("allow_loopback", False) is True

    for item in allowed:
        permitted = _parse_ip(item)
        if permitted is not None and permitted == address:
            return True

    # Unknown IPs are denied by default.
    return False


def is_allowed_port(port: int, config: dict[str, Any]) -> bool:
    """Check whether a destination port is explicitly permitted."""
    if type(port) is not int or not 1 <= port <= 65535:
        return False

    network = config.get("network_protection", config)
    if not isinstance(network, dict):
        return False

    allowed_ports = network.get("allowed_ports", [])

    if not isinstance(allowed_ports, list):
        return False

    return any(
        type(item) is int and item == port
        for item in allowed_ports
    )


def evaluate_access(
    client_ip: str,
    port: int,
    config: dict[str, Any],
) -> dict[str, Any]:
    """
    Evaluate an access request without opening or blocking connections.
    """
    ip_allowed = is_allowed_ip(client_ip, config)
    port_allowed = is_allowed_port(port, config)

    allowed = ip_allowed and port_allowed

    return {
        "decision": "allow" if allowed else "deny",
        "ip_allowed": ip_allowed,
        "port_allowed": port_allowed,
        "default_policy": "deny",
        "enforcement": "policy_check_only",
        "system_firewall_changed": False,
    }
