
"""
Tamanna AI - Unicornscan Tool Adapter
Owner: HM INSAN ALI

Tool:
    unicornscan 0.4.7

Purpose:
    Integrate Unicornscan into Tamanna AI's central
    tool-routing and capability system.

Safety:
    - Execution disabled by default.
    - Explicit authorization required.
    - Only authorized/owned targets.
    - No source-code modification.
    - Sensitive network options are explicitly marked.
"""

from __future__ import annotations

import ipaddress
import json
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any


TOOL_NAME = "unicornscan"
TOOL_VERSION = "0.4.7"

EXECUTION_ENABLED = False

DEFAULT_PACKET_TIMEOUT = 7

CAPABILITIES = {
    "tcp_scanning": [
        "tcp scan",
        "tcp scanning",
        "syn scan",
        "tcp syn",
        "tcp connect",
    ],
    "udp_scanning": [
        "udp scan",
        "udp scanning",
    ],
    "arp_scanning": [
        "arp scan",
        "arp scanning",
    ],
    "port_scanning": [
        "port scan",
        "port scanning",
        "scan ports",
        "open ports",
    ],
    "os_fingerprinting": [
        "os fingerprint",
        "os fingerprinting",
        "operating system detection",
    ],
    "dns_resolution": [
        "dns",
        "resolve hostname",
        "hostname resolution",
    ],
    "packet_capture": [
        "pcap",
        "packet capture",
        "capture packets",
    ],
    "traffic_sniffing": [
        "sniff",
        "sniffing",
        "traffic sniffing",
    ],
    "network_discovery": [
        "network discovery",
        "host discovery",
        "network scan",
    ],
    "reporting": [
        "report",
        "reporting",
        "output",
        "log",
    ],
}


OPTIONS = {
    "-b": {
        "long": "--broken-crc",
        "description": "Set broken CRC sums.",
        "category": "packet",
        "requires_argument": True,
        "sensitive": True,
    },
    "-B": {
        "long": "--source-port",
        "description": "Set source port.",
        "category": "network",
        "requires_argument": True,
        "sensitive": True,
    },
    "-c": {
        "long": "--proc-duplicates",
        "description": "Process duplicate replies.",
        "category": "processing",
        "requires_argument": False,
    },
    "-d": {
        "long": "--delay-type",
        "description": "Select delay type.",
        "category": "timing",
        "requires_argument": True,
    },
    "-D": {
        "long": "--no-defpayload",
        "description": "Disable default payload.",
        "category": "payload",
        "requires_argument": False,
    },
    "-e": {
        "long": "--enable-module",
        "description": "Enable output/report modules.",
        "category": "modules",
        "requires_argument": True,
    },
    "-E": {
        "long": "--proc-errors",
        "description": "Process non-open responses.",
        "category": "processing",
        "requires_argument": False,
    },
    "-F": {
        "long": "--try-frags",
        "description": "Try packet fragmentation.",
        "category": "evasion",
        "requires_argument": False,
        "sensitive": True,
    },
    "-G": {
        "long": "--payload-group",
        "description": "Select payload group.",
        "category": "payload",
        "requires_argument": True,
    },
    "-H": {
        "long": "--do-dns",
        "description": "Resolve hostnames during reporting.",
        "category": "dns",
        "requires_argument": False,
    },
    "-i": {
        "long": "--interface",
        "description": "Select network interface.",
        "category": "network",
        "requires_argument": True,
        "sensitive": True,
    },
    "-I": {
        "long": "--immediate",
        "description": "Display results immediately.",
        "category": "output",
        "requires_argument": False,
    },
    "-j": {
        "long": "--ignore-seq",
        "description": "Ignore TCP sequence validation.",
        "category": "tcp",
        "requires_argument": False,
        "sensitive": True,
    },
    "-l": {
        "long": "--logfile",
        "description": "Write output to logfile.",
        "category": "output",
        "requires_argument": True,
    },
    "-L": {
        "long": "--packet-timeout",
        "description": "Packet response timeout.",
        "category": "timing",
        "requires_argument": True,
    },
    "-m": {
        "long": "--mode",
        "description": "Select scan mode.",
        "category": "scan",
        "requires_argument": True,
    },
    "-M": {
        "long": "--module-dir",
        "description": "Module directory.",
        "category": "modules",
        "requires_argument": True,
    },
    "-o": {
        "long": "--format",
        "description": "Output format.",
        "category": "output",
        "requires_argument": True,
    },
    "-p": {
        "long": "--ports",
        "description": "Ports to scan.",
        "category": "ports",
        "requires_argument": True,
    },
    "-P": {
        "long": "--pcap-filter",
        "description": "Additional pcap filter.",
        "category": "packet",
        "requires_argument": True,
        "sensitive": True,
    },
    "-q": {
        "long": "--covertness",
        "description": "Covertness value 0-255.",
        "category": "evasion",
        "requires_argument": True,
        "sensitive": True,
    },
    "-Q": {
        "long": "--quiet",
        "description": "Suppress screen output.",
        "category": "output",
        "requires_argument": False,
    },
    "-r": {
        "long": "--pps",
        "description": "Packets per second.",
        "category": "performance",
        "requires_argument": True,
        "sensitive": True,
    },
    "-R": {
        "long": "--repeats",
        "description": "Repeat packet scan N times.",
        "category": "performance",
        "requires_argument": True,
    },
    "-s": {
        "long": "--source-addr",
        "description": "Set source address.",
        "category": "network",
        "requires_argument": True,
        "sensitive": True,
    },
    "-S": {
        "long": "--no-shuffle",
        "description": "Do not shuffle ports.",
        "category": "scan",
        "requires_argument": False,
    },
    "-t": {
        "long": "--ip-ttl",
        "description": "Set IP TTL.",
        "category": "network",
        "requires_argument": True,
        "sensitive": True,
    },
    "-T": {
        "long": "--ip-tos",
        "description": "Set IP TOS.",
        "category": "network",
        "requires_argument": True,
        "sensitive": True,
    },
    "-u": {
        "long": "--debug",
        "description": "Debug mask.",
        "category": "debug",
        "requires_argument": True,
    },
    "-U": {
        "long": "--no-openclosed",
        "description": "Do not report open/closed state.",
        "category": "output",
        "requires_argument": False,
    },
    "-w": {
        "long": "--safefile",
        "description": "Write received packets to pcap.",
        "category": "capture",
        "requires_argument": True,
    },
    "-W": {
        "long": "--fingerprint",
        "description": "OS fingerprint profile.",
        "category": "fingerprinting",
        "requires_argument": True,
    },
    "-v": {
        "long": "--verbose",
        "description": "Increase verbosity.",
        "category": "output",
        "requires_argument": False,
    },
    "-V": {
        "long": "--version",
        "description": "Display version.",
        "category": "general",
        "requires_argument": False,
    },
    "-z": {
        "long": "--sniff",
        "description": "Sniff alike.",
        "category": "sniffing",
        "requires_argument": False,
        "sensitive": True,
    },
    "-Z": {
        "long": "--drone-str",
        "description": "Drone string.",
        "category": "distributed",
        "requires_argument": True,
        "sensitive": True,
    },
}


SENSITIVE_OPTIONS = {
    "-b",
    "-B",
    "-F",
    "-i",
    "-j",
    "-P",
    "-q",
    "-r",
    "-s",
    "-t",
    "-T",
    "-z",
    "-Z",
}


# ------------------------------------------------------------
# BINARY / STATUS
# ------------------------------------------------------------

def find_binary() -> str | None:
    candidates = [
        shutil.which("unicornscan"),
        "/usr/bin/unicornscan",
        "/usr/local/bin/unicornscan",
    ]

    for candidate in candidates:
        if candidate and Path(candidate).exists():
            return str(candidate)

    return None


def status() -> dict[str, Any]:
    binary = find_binary()

    result = {
        "tool": TOOL_NAME,
        "version": TOOL_VERSION,
        "installed": binary is not None,
        "binary": binary,
        "execution_enabled": EXECUTION_ENABLED,
        "authorization_required": True,
    }

    if binary:
        try:
            proc = subprocess.run(
                [binary, "-V"],
                capture_output=True,
                text=True,
                timeout=10,
            )

            result["return_code"] = proc.returncode
            result["version_output"] = (
                proc.stdout.strip()
                or proc.stderr.strip()
            )

        except Exception as exc:
            result["error"] = str(exc)

    return result


# ------------------------------------------------------------
# TARGET VALIDATION
# ------------------------------------------------------------

def validate_target(target: str) -> dict[str, Any]:
    if not isinstance(target, str):
        return {
            "valid": False,
            "error": "Target must be a string.",
        }

    target = target.strip()

    if not target:
        return {
            "valid": False,
            "error": "Target is empty.",
        }

    if len(target) > 255:
        return {
            "valid": False,
            "error": "Target is too long.",
        }

    # Prevent shell injection.
    dangerous = [
        ";",
        "|",
        "&",
        "`",
        "$(",
        "&&",
        "||",
        "\n",
        "\r",
        ">",
        "<",
    ]

    for item in dangerous:
        if item in target:
            return {
                "valid": False,
                "error": f"Unsafe target sequence: {item!r}",
            }

    # CIDR / IP validation.
    try:
        network = ipaddress.ip_network(
            target,
            strict=False,
        )

        return {
            "valid": True,
            "target": target,
            "target_type": "network",
            "network": str(network),
        }

    except ValueError:
        pass

    # Hostname validation.
    hostname_pattern = (
        r"^(?=.{1,253}$)"
        r"(?:[A-Za-z0-9]"
        r"(?:[A-Za-z0-9-]{0,61}"
        r"[A-Za-z0-9])?\.)+"
        r"[A-Za-z]{2,63}$"
    )

    if re.fullmatch(hostname_pattern, target):
        return {
            "valid": True,
            "target": target,
            "target_type": "hostname",
        }

    return {
        "valid": False,
        "error": (
            "Target must be an IP, CIDR network, "
            "or valid hostname."
        ),
    }


# ------------------------------------------------------------
# PORT SPECIFICATION
# ------------------------------------------------------------

def validate_ports(ports: str) -> dict[str, Any]:
    if not isinstance(ports, str):
        return {
            "valid": False,
            "error": "Ports must be a string.",
        }

    ports = ports.strip()

    if not ports:
        return {
            "valid": False,
            "error": "Port specification is empty.",
        }

    # Supported Unicornscan forms from supplied help:
    # 53
    # 1-4096
    # a
    # p
    if ports in {"a", "p"}:
        return {
            "valid": True,
            "ports": ports,
        }

    if re.fullmatch(r"\d+", ports):
        value = int(ports)

        if not 1 <= value <= 65535:
            return {
                "valid": False,
                "error": "Port must be 1-65535.",
            }

        return {
            "valid": True,
            "ports": ports,
        }

    match = re.fullmatch(
        r"(\d+)-(\d+)",
        ports,
    )

    if match:
        start = int(match.group(1))
        end = int(match.group(2))

        if not (
            1 <= start <= 65535
            and 1 <= end <= 65535
            and start <= end
        ):
            return {
                "valid": False,
                "error": "Invalid port range.",
            }

        return {
            "valid": True,
            "ports": ports,
        }

    return {
        "valid": False,
        "error": (
            "Unsupported port specification. "
            "Use a port, range, a, or p."
        ),
    }


# ------------------------------------------------------------
# CAPABILITY ROUTING
# ------------------------------------------------------------

def match_capability(
    request: str,
) -> list[dict[str, Any]]:

    if not isinstance(request, str):
        return []

    text = request.lower()
    matches = []

    for capability, keywords in CAPABILITIES.items():
        matched = [
            keyword
            for keyword in keywords
            if keyword.lower() in text
        ]

        if matched:
            matches.append(
                {
                    "capability": capability,
                    "score": len(matched),
                    "matched_keywords": matched,
                }
            )

    matches.sort(
        key=lambda item: item["score"],
        reverse=True,
    )

    return matches


def classify(request: str) -> dict[str, Any]:
    matches = match_capability(request)

    return {
        "tool": TOOL_NAME,
        "request": request,
        "matched": bool(matches),
        "matches": matches,
    }


def classify_option(option: str) -> dict[str, Any]:
    if option in OPTIONS:
        return {
            "found": True,
            "option": option,
            **OPTIONS[option],
        }

    for short, info in OPTIONS.items():
        if info.get("long") == option:
            return {
                "found": True,
                "option": option,
                "short": short,
                **info,
            }

    return {
        "found": False,
        "option": option,
    }


# ------------------------------------------------------------
# COMMAND PREPARATION
# ------------------------------------------------------------

def prepare(
    target: str,
    ports: str | None = None,
    mode: str = "T",
    interface: str | None = None,
    packet_rate: int | None = None,
    packet_timeout: int = DEFAULT_PACKET_TIMEOUT,
    fingerprint: int | None = None,
    dns: bool = False,
    immediate: bool = True,
    verbose: int = 0,
    logfile: str | None = None,
    pcap_file: str | None = None,
) -> dict[str, Any]:

    target_result = validate_target(target)

    if not target_result["valid"]:
        return {
            "ok": False,
            "error": target_result["error"],
        }

    if ports is not None:
        ports_result = validate_ports(ports)

        if not ports_result["valid"]:
            return {
                "ok": False,
                "error": ports_result["error"],
            }

    if not isinstance(packet_timeout, int):
        return {
            "ok": False,
            "error": "Packet timeout must be an integer.",
        }

    if packet_timeout < 1:
        return {
            "ok": False,
            "error": "Packet timeout must be >= 1.",
        }

    if packet_rate is not None:
        if not isinstance(packet_rate, int):
            return {
                "ok": False,
                "error": "Packet rate must be an integer.",
            }

        if packet_rate < 1:
            return {
                "ok": False,
                "error": "Packet rate must be >= 1.",
            }

    if fingerprint is not None:
        if fingerprint not in range(0, 8):
            return {
                "ok": False,
                "error": (
                    "Fingerprint profile must be 0-7."
                ),
            }

    if mode not in {
        "T",
        "U",
        "sf",
        "A",
    }:
        return {
            "ok": False,
            "error": (
                "Supported safe mode values: "
                "T, U, sf, A."
            ),
        }

    binary = find_binary()

    if not binary:
        return {
            "ok": False,
            "error": "unicornscan executable not found.",
        }

    command = [
        binary,
        "-m",
        mode,
    ]

    if ports:
        command.extend([
            "-p",
            ports,
        ])

    command.extend([
        "-L",
        str(packet_timeout),
    ])

    if interface:
        command.extend([
            "-i",
            interface,
        ])

    if packet_rate is not None:
        command.extend([
            "-r",
            str(packet_rate),
        ])

    if fingerprint is not None:
        command.extend([
            "-W",
            str(fingerprint),
        ])

    if dns:
        command.append("-H")

    if immediate:
        command.append("-I")

    if verbose:
        command.extend(
            ["-v"] * min(verbose, 5)
        )

    if logfile:
        log_path = Path(logfile).expanduser().resolve()
        log_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )
        command.extend([
            "-l",
            str(log_path),
        ])

    if pcap_file:
        pcap_path = Path(pcap_file).expanduser().resolve()
        pcap_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )
        command.extend([
            "-w",
            str(pcap_path),
        ])

    command.append(target)

    # Conservative prepared command metadata.
    return {
        "ok": True,
        "tool": TOOL_NAME,
        "version": TOOL_VERSION,
        "target": target,
        "ports": ports,
        "mode": mode,
        "command": command,
        "execution_enabled": EXECUTION_ENABLED,
        "authorization_required": True,
        "sensitive_options_available": sorted(
            SENSITIVE_OPTIONS
        ),
    }


# ------------------------------------------------------------
# SAFE PRESETS
# ------------------------------------------------------------

def prepare_tcp(
    target: str,
    ports: str = "1-1024",
) -> dict[str, Any]:
    return prepare(
        target=target,
        ports=ports,
        mode="T",
        packet_timeout=DEFAULT_PACKET_TIMEOUT,
        immediate=True,
    )


def prepare_udp(
    target: str,
    ports: str = "1-1024",
) -> dict[str, Any]:
    return prepare(
        target=target,
        ports=ports,
        mode="U",
        packet_timeout=DEFAULT_PACKET_TIMEOUT,
        immediate=True,
    )


def prepare_arp(
    target: str,
) -> dict[str, Any]:
    return prepare(
        target=target,
        mode="A",
        packet_timeout=DEFAULT_PACKET_TIMEOUT,
        immediate=True,
    )


def prepare_fingerprint(
    target: str,
    ports: str = "1-1024",
) -> dict[str, Any]:
    return prepare(
        target=target,
        ports=ports,
        mode="T",
        fingerprint=5,
        packet_timeout=DEFAULT_PACKET_TIMEOUT,
        immediate=True,
    )


# ------------------------------------------------------------
# KNOWLEDGE EXPORT
# ------------------------------------------------------------

def export_knowledge(
    output_file: str | None = None,
) -> dict[str, Any]:

    if output_file is None:
        output_file = str(
            Path(__file__).resolve().parent
            / "unicornscan_knowledge.json"
        )

    data = {
        "tool": TOOL_NAME,
        "version": TOOL_VERSION,
        "description": (
            "Unicornscan asynchronous network "
            "and port scanning utility."
        ),
        "options": OPTIONS,
        "capabilities": CAPABILITIES,
        "sensitive_options": sorted(
            SENSITIVE_OPTIONS
        ),
        "execution_enabled": EXECUTION_ENABLED,
        "authorization_required": True,
        "owner": "HM INSAN ALI",
    }

    path = Path(output_file).expanduser().resolve()
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    path.write_text(
        json.dumps(
            data,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    return {
        "ok": True,
        "file": str(path),
        "tool": TOOL_NAME,
        "version": TOOL_VERSION,
    }


# ------------------------------------------------------------
# EXECUTION
# ------------------------------------------------------------

def run(
    target: str,
    authorized: bool = False,
    execution_enabled: bool = False,
    **kwargs: Any,
) -> dict[str, Any]:

    if not authorized:
        return {
            "ok": False,
            "executed": False,
            "error": (
                "Authorization required. "
                "Use Unicornscan only against "
                "owned/authorized targets."
            ),
        }

    if not execution_enabled:
        return {
            "ok": False,
            "executed": False,
            "error": (
                "Execution is disabled by default. "
                "Set execution_enabled=True explicitly."
            ),
        }

    prepared = prepare(
        target=target,
        **kwargs,
    )

    if not prepared.get("ok"):
        return prepared

    command = prepared["command"]

    try:
        proc = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=600,
        )

        return {
            "ok": proc.returncode == 0,
            "executed": True,
            "return_code": proc.returncode,
            "stdout": proc.stdout,
            "stderr": proc.stderr,
        }

    except subprocess.TimeoutExpired:
        return {
            "ok": False,
            "executed": True,
            "error": "Unicornscan execution timed out.",
        }

    except Exception as exc:
        return {
            "ok": False,
            "executed": False,
            "error": str(exc),
        }


# ------------------------------------------------------------
# TAMANNA ROUTER BRIDGES
# ------------------------------------------------------------

def unicornscan_status():
    return status()


def unicornscan_validate_target(target):
    return validate_target(target)


def unicornscan_validate_ports(ports):
    return validate_ports(ports)


def unicornscan_classify(request):
    return classify(request)


def unicornscan_match_capability(request):
    return match_capability(request)


def unicornscan_classify_option(option):
    return classify_option(option)


def unicornscan_prepare(target, **kwargs):
    return prepare(target, **kwargs)


def unicornscan_prepare_tcp(
    target,
    ports="1-1024",
):
    return prepare_tcp(target, ports)


def unicornscan_prepare_udp(
    target,
    ports="1-1024",
):
    return prepare_udp(target, ports)


def unicornscan_prepare_arp(target):
    return prepare_arp(target)


def unicornscan_prepare_fingerprint(
    target,
    ports="1-1024",
):
    return prepare_fingerprint(
        target,
        ports,
    )


def unicornscan_export_knowledge(
    output_file=None,
):
    return export_knowledge(output_file)


def unicornscan_run(
    target,
    authorized=False,
    execution_enabled=False,
    **kwargs,
):
    return run(
        target=target,
        authorized=authorized,
        execution_enabled=execution_enabled,
        **kwargs,
    )


# ------------------------------------------------------------
# DIRECT TEST
# ------------------------------------------------------------

if __name__ == "__main__":

    print("🥰 Tamanna AI - Unicornscan Adapter")
    print("Owner: HM INSAN ALI")
    print(f"Version: {TOOL_VERSION}")
    print()

    print("=== STATUS ===")
    print(
        json.dumps(
            status(),
            indent=2,
            ensure_ascii=False,
        )
    )

    print()
    print("=== TARGET TEST ===")
    print(
        json.dumps(
            validate_target("192.168.1.0/24"),
            indent=2,
        )
    )

    print()
    print("=== PORT TEST ===")
    print(
        json.dumps(
            validate_ports("1-1024"),
            indent=2,
        )
    )

    print()
    print("=== CAPABILITY TEST ===")
    print(
        json.dumps(
            classify(
                "scan TCP ports and fingerprint "
                "the operating system"
            ),
            indent=2,
            ensure_ascii=False,
        )
    )

    print()
    print("=== OPTION TEST ===")
    print(
        json.dumps(
            classify_option("--fingerprint"),
            indent=2,
            ensure_ascii=False,
        )
    )

    print()
    print("=== PREPARE TEST ===")
    print(
        json.dumps(
            prepare_tcp(
                "192.168.1.1",
                "1-1024",
            ),
            indent=2,
            ensure_ascii=False,
        )
    )

    print()
    print("=== KNOWLEDGE EXPORT ===")
    print(
        json.dumps(
            export_knowledge(),
            indent=2,
            ensure_ascii=False,
        )
    )

    print()
    print("=== EXECUTION POLICY ===")
    print(
        json.dumps(
            {
                "execution_enabled":
                    EXECUTION_ENABLED,
                "authorization_required": True,
            },
            indent=2,
        )
    )
PY