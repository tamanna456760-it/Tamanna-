
"""
Tamanna AI — Advanced Network Port Checker
Owner: HM INSAN ALI

Read-only TCP listening-port inspection.
Does not scan external hosts or change firewall rules.
"""

from __future__ import annotations

import json
import shutil
import socket
import subprocess
from datetime import datetime, timezone
from typing import Any


def inspect_tcp_ports(timeout: int = 10) -> dict[str, Any]:
    """Inspect local TCP listening sockets using the ss utility."""
    if not isinstance(timeout, int) or not 1 <= timeout <= 30:
        return {
            "ok": False,
            "error": "Timeout must be between 1 and 30 seconds.",
            "ports": [],
        }

    if not shutil.which("ss"):
        return {
            "ok": False,
            "error": "'ss' is unavailable on this system.",
            "ports": [],
        }

    try:
        result = subprocess.run(
            ["ss", "-H", "-lnt"],
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return {
            "ok": False,
            "error": "Port inspection timed out.",
            "ports": [],
        }
    except OSError:
        return {
            "ok": False,
            "error": "Unable to execute local port inspection.",
            "ports": [],
        }

    if result.returncode != 0:
        return {
            "ok": False,
            "error": "The local port inspection command failed.",
            "ports": [],
        }

    ports = []

    for line in result.stdout.splitlines():
        fields = line.split()
        if len(fields) < 4:
            continue

        local_address = fields[3]
        port_text = local_address.rsplit(":", 1)[-1]

        try:
            port = int(port_text)
        except ValueError:
            continue

        ports.append({
            "protocol": "tcp",
            "local_address": local_address,
            "port": port,
        })

    return {
        "ok": True,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "scope": "local_host_only",
        "count": len(ports),
        "ports": ports,
        "firewall_rules_changed": False,
    }


def classify_port(port: int) -> str:
    """Provide a basic review hint, not a vulnerability verdict."""
    if type(port) is not int or not 1 <= port <= 65535:
        return "invalid_port"

    common_services = {
        22: "SSH — verify key-based authentication and access restrictions",
        53: "DNS — verify whether public DNS service is intended",
        80: "HTTP — verify whether public web access is intended",
        443: "HTTPS — verify TLS and application security",
        8000: "Development/API port — avoid public exposure unless required",
        8080: "Alternative web/API port — review access requirements",
        5432: "PostgreSQL — keep private unless access is explicitly required",
        3306: "MySQL — keep private unless access is explicitly required",
        6379: "Redis — restrict to trusted services",
    }

    return common_services.get(
        port,
        "Review the service, its owner, and its required network exposure",
    )


def generate_report() -> dict[str, Any]:
    """Combine local port inspection with review guidance."""
    result = inspect_tcp_ports()

    if not result["ok"]:
        return result

    for item in result["ports"]:
        item["review"] = classify_port(item["port"])

    result["recommendation"] = (
        "Review each listening service. A listening port alone "
        "does not prove that a service is vulnerable or publicly reachable."
    )
    return result


if __name__ == "__main__":
    print(json.dumps(generate_report(), indent=2, ensure_ascii=False))
