
"""
Tamanna AI - MSFPC Tool Knowledge Adapter
Tool: MSFvenom Payload Creator (MSFPC)
Version: 1.4.5

Owner: HM INSAN ALI

SAFE MODE:
- Knowledge / status / help / classification / validation only
- No payload generation
- No reverse/bind shell creation
- No listener setup
- No target execution
- No automatic exploitation
- No source-code modification
"""

from __future__ import annotations

import re
import shutil
import subprocess
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional


TOOL_NAME = "msfpc"
TOOL_DISPLAY_NAME = "MSFvenom Payload Creator (MSFPC)"
TOOL_VERSION = "1.4.5"

EXECUTION_ENABLED = False
PAYLOAD_GENERATION_ENABLED = False
TARGET_EXECUTION_ENABLED = False


# ---------------------------------------------------------
# MSFPC KNOWLEDGE
# ---------------------------------------------------------

PAYLOAD_TYPES: Dict[str, Dict[str, Any]] = {
    "apk": {
        "name": "APK",
        "platform": "Android",
        "extension": ".apk",
    },
    "asp": {
        "name": "ASP",
        "platform": "Web",
        "extension": ".asp",
    },
    "aspx": {
        "name": "ASPX",
        "platform": "Web",
        "extension": ".aspx",
    },
    "bash": {
        "name": "Bash",
        "platform": "Linux/Unix",
        "extension": ".sh",
    },
    "java": {
        "name": "Java",
        "platform": "Java/Web",
        "extension": ".jsp",
    },
    "linux": {
        "name": "Linux",
        "platform": "Linux",
        "extension": ".elf",
    },
    "osx": {
        "name": "OSX",
        "platform": "macOS",
        "extension": ".macho",
    },
    "perl": {
        "name": "Perl",
        "platform": "Cross-platform/Web",
        "extension": ".pl",
    },
    "php": {
        "name": "PHP",
        "platform": "Web",
        "extension": ".php",
    },
    "powershell": {
        "name": "Powershell",
        "platform": "Windows",
        "extension": ".ps1",
    },
    "python": {
        "name": "Python",
        "platform": "Cross-platform",
        "extension": ".py",
    },
    "tomcat": {
        "name": "Tomcat",
        "platform": "Java/Tomcat",
        "extension": ".war",
    },
    "windows": {
        "name": "Windows",
        "platform": "Windows",
        "extension": ".exe/.dll",
    },
}


COMMAND_MODES = {
    "cmd": {
        "description": "Standard/native command prompt or terminal.",
    },
    "msf": {
        "description": "Metasploit-oriented command mode.",
    },
}


CONNECTION_MODES = {
    "bind": {
        "description": "Bind-style connection model.",
    },
    "reverse": {
        "description": "Reverse-style connection model.",
    },
}


PAYLOAD_MODES = {
    "staged": {
        "description": "Payload is split into stages and depends on the framework.",
    },
    "stageless": {
        "description": "Payload is represented as a complete standalone payload.",
    },
}


TRANSPORTS = {
    "tcp": {
        "description": "Standard TCP transport.",
    },
    "http": {
        "description": "HTTP transport.",
    },
    "https": {
        "description": "HTTPS transport.",
    },
    "find_port": {
        "aliases": ["find-port", "find_port"],
        "description": "Port-discovery style transport mode.",
    },
}


SPECIAL_MODES = {
    "batch": {
        "description": "Batch mode for combinations.",
    },
    "loop": {
        "description": "Loop mode across supported types.",
    },
    "verbose": {
        "description": "Verbose information mode.",
    },
    "help": {
        "description": "Help/information mode.",
    },
}


DEFAULTS = {
    "port": 443,
    "connection": "reverse",
    "transport": "tcp",
    "command_mode": "msf",
    "payload_mode": "staged",
}


CAPABILITIES = {
    "msfpc": [
        "msfpc",
        "msfvenom payload creator",
        "metasploit payload tool",
    ],
    "payload_type_detection": [
        "payload type",
        "type detection",
        "apk",
        "asp",
        "aspx",
        "bash",
        "java",
        "linux",
        "osx",
        "perl",
        "php",
        "powershell",
        "python",
        "tomcat",
        "windows",
    ],
    "platform_mapping": [
        "android",
        "linux",
        "windows",
        "macos",
        "web",
        "java",
        "cross platform",
    ],
    "command_mode_understanding": [
        "cmd",
        "msf",
        "command mode",
    ],
    "connection_mode_understanding": [
        "bind",
        "reverse",
        "connection",
    ],
    "staging_understanding": [
        "staged",
        "stageless",
        "staging",
    ],
    "transport_understanding": [
        "tcp",
        "http",
        "https",
        "find port",
        "transport",
    ],
    "batch_loop_understanding": [
        "batch",
        "loop",
        "combination",
    ],
    "tool_help": [
        "help",
        "usage",
        "documentation",
    ],
}


@dataclass
class ValidationResult:
    ok: bool
    field: str
    value: Any
    message: str


# ---------------------------------------------------------
# STATUS
# ---------------------------------------------------------

def status() -> Dict[str, Any]:
    """
    Return MSFPC adapter status.

    This does NOT execute MSFPC payload-generation commands.
    """
    binary = shutil.which("msfpc")

    return {
        "ok": True,
        "tool": TOOL_NAME,
        "display_name": TOOL_DISPLAY_NAME,
        "version": TOOL_VERSION,
        "binary_found": binary is not None,
        "binary_path": binary,
        "execution_enabled": EXECUTION_ENABLED,
        "payload_generation_enabled": PAYLOAD_GENERATION_ENABLED,
        "target_execution_enabled": TARGET_EXECUTION_ENABLED,
        "safe_mode": True,
        "owner": "HM INSAN ALI",
    }


# ---------------------------------------------------------
# HELP
# ---------------------------------------------------------

def help_info() -> Dict[str, Any]:
    return {
        "ok": True,
        "tool": TOOL_NAME,
        "version": TOOL_VERSION,
        "usage": "/usr/bin/msfpc <TYPE> (<DOMAIN/IP>) (<PORT>) "
                 "(<CMD/MSF>) (<BIND/REVERSE>) "
                 "(<STAGED/STAGELESS>) "
                 "(<TCP/HTTP/HTTPS/FIND_PORT>) "
                 "(<BATCH/LOOP>) (<VERBOSE>)",
        "types": sorted(PAYLOAD_TYPES.keys()),
        "command_modes": sorted(COMMAND_MODES.keys()),
        "connection_modes": sorted(CONNECTION_MODES.keys()),
        "payload_modes": sorted(PAYLOAD_MODES.keys()),
        "transports": sorted(TRANSPORTS.keys()),
        "special_modes": sorted(SPECIAL_MODES.keys()),
        "defaults": DEFAULTS.copy(),
    }


# ---------------------------------------------------------
# TYPE / OPTION CLASSIFICATION
# ---------------------------------------------------------

def classify(value: str) -> Dict[str, Any]:
    """
    Classify a user-provided MSFPC token.

    Safe: this only identifies the token category.
    """

    if not isinstance(value, str):
        return {
            "ok": False,
            "error": "value must be a string",
        }

    token = value.strip().lower()

    if token in PAYLOAD_TYPES:
        return {
            "ok": True,
            "value": value,
            "category": "payload_type",
            "normalized": token,
            "details": PAYLOAD_TYPES[token],
        }

    if token in COMMAND_MODES:
        return {
            "ok": True,
            "value": value,
            "category": "command_mode",
            "normalized": token,
            "details": COMMAND_MODES[token],
        }

    if token in CONNECTION_MODES:
        return {
            "ok": True,
            "value": value,
            "category": "connection_mode",
            "normalized": token,
            "details": CONNECTION_MODES[token],
        }

    if token in PAYLOAD_MODES:
        return {
            "ok": True,
            "value": value,
            "category": "payload_mode",
            "normalized": token,
            "details": PAYLOAD_MODES[token],
        }

    if token in TRANSPORTS:
        return {
            "ok": True,
            "value": value,
            "category": "transport",
            "normalized": token,
            "details": TRANSPORTS[token],
        }

    if token in {"find-port", "find_port"}:
        return {
            "ok": True,
            "value": value,
            "category": "transport",
            "normalized": "find_port",
            "details": TRANSPORTS["find_port"],
        }

    if token in SPECIAL_MODES:
        return {
            "ok": True,
            "value": value,
            "category": "special_mode",
            "normalized": token,
            "details": SPECIAL_MODES[token],
        }

    if token.isdigit():
        return {
            "ok": True,
            "value": value,
            "category": "port",
            "normalized": int(token),
            "details": {
                "description": "Numeric port value.",
            },
        }

    if re.fullmatch(r"[a-zA-Z0-9_.:-]+", token):
        return {
            "ok": True,
            "value": value,
            "category": "host_or_identifier",
            "normalized": token,
            "details": {
                "description": "Potential host/interface/identifier.",
            },
        }

    return {
        "ok": False,
        "value": value,
        "category": "unknown",
        "message": "Token is not recognized by the MSFPC knowledge layer.",
    }


# ---------------------------------------------------------
# VALIDATORS
# ---------------------------------------------------------

def validate_type(payload_type: str) -> ValidationResult:
    normalized = str(payload_type).strip().lower()

    if normalized in PAYLOAD_TYPES:
        return ValidationResult(
            True,
            "type",
            payload_type,
            "Supported MSFPC payload type.",
        )

    return ValidationResult(
        False,
        "type",
        payload_type,
        "Unsupported MSFPC type.",
    )


def validate_port(port: Any) -> ValidationResult:
    try:
        value = int(port)
    except (TypeError, ValueError):
        return ValidationResult(
            False,
            "port",
            port,
            "Port must be an integer.",
        )

    if not 1 <= value <= 65535:
        return ValidationResult(
            False,
            "port",
            port,
            "Port must be between 1 and 65535.",
        )

    return ValidationResult(
        True,
        "port",
        value,
        "Valid TCP/HTTP/HTTPS port range.",
    )


def validate_connection(connection: str) -> ValidationResult:
    value = str(connection).strip().lower()

    if value in CONNECTION_MODES:
        return ValidationResult(
            True,
            "connection",
            value,
            "Supported connection mode.",
        )

    return ValidationResult(
        False,
        "connection",
        connection,
        "Use bind or reverse.",
    )


def validate_payload_mode(mode: str) -> ValidationResult:
    value = str(mode).strip().lower()

    if value in PAYLOAD_MODES:
        return ValidationResult(
            True,
            "payload_mode",
            value,
            "Supported staged/stageless mode.",
        )

    return ValidationResult(
        False,
        "payload_mode",
        mode,
        "Use staged or stageless.",
    )


def validate_transport(transport: str) -> ValidationResult:
    value = str(transport).strip().lower()

    if value in {"tcp", "http", "https", "find_port", "find-port"}:
        normalized = "find_port" if value == "find-port" else value

        return ValidationResult(
            True,
            "transport",
            normalized,
            "Supported transport mode.",
        )

    return ValidationResult(
        False,
        "transport",
        transport,
        "Use tcp, http, https, or find_port.",
    )


# ---------------------------------------------------------
# CAPABILITY MATCHING
# ---------------------------------------------------------

def match_capability(text: str) -> Dict[str, Any]:
    """
    Match natural-language intent to MSFPC knowledge categories.

    No command is executed.
    """

    if not isinstance(text, str):
        return {
            "ok": False,
            "matches": [],
        }

    query = text.lower()
    matches: List[Dict[str, Any]] = []

    for capability, keywords in CAPABILITIES.items():
        hits = [
            keyword
            for keyword in keywords
            if keyword.lower() in query
        ]

        if hits:
            matches.append({
                "capability": capability,
                "matched_keywords": hits,
            })

    return {
        "ok": True,
        "query": text,
        "matches": matches,
        "safe_mode": True,
    }


# ---------------------------------------------------------
# SAFE ANALYSIS / PREPARATION
# ---------------------------------------------------------

def analyze_request(
    payload_type: Optional[str] = None,
    port: Optional[Any] = None,
    command_mode: Optional[str] = None,
    connection: Optional[str] = None,
    payload_mode: Optional[str] = None,
    transport: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Analyze an MSFPC request without constructing or executing
    a payload-generation command.
    """

    result: Dict[str, Any] = {
        "ok": True,
        "tool": TOOL_NAME,
        "version": TOOL_VERSION,
        "safe_mode": True,
        "payload_generation_requested": bool(payload_type),
        "execution_requested": False,
        "validations": [],
        "resolved": {},
    }

    if payload_type is not None:
        validation = validate_type(payload_type)
        result["validations"].append(asdict(validation))

        if validation.ok:
            result["resolved"]["type"] = validation.value

    if port is not None:
        validation = validate_port(port)
        result["validations"].append(asdict(validation))

        if validation.ok:
            result["resolved"]["port"] = validation.value

    if command_mode is not None:
        value = str(command_mode).strip().lower()

        if value in COMMAND_MODES:
            result["resolved"]["command_mode"] = value
            result["validations"].append({
                "ok": True,
                "field": "command_mode",
                "value": value,
                "message": "Supported command mode.",
            })
        else:
            result["validations"].append({
                "ok": False,
                "field": "command_mode",
                "value": command_mode,
                "message": "Use cmd or msf.",
            })

    if connection is not None:
        validation = validate_connection(connection)
        result["validations"].append(asdict(validation))

        if validation.ok:
            result["resolved"]["connection"] = validation.value

    if payload_mode is not None:
        validation = validate_payload_mode(payload_mode)
        result["validations"].append(asdict(validation))

        if validation.ok:
            result["resolved"]["payload_mode"] = validation.value

    if transport is not None:
        validation = validate_transport(transport)
        result["validations"].append(asdict(validation))

        if validation.ok:
            result["resolved"]["transport"] = validation.value

    result["defaults"] = DEFAULTS.copy()

    # Important safety boundary:
    result["action"] = (
        "Knowledge analysis only. "
        "No payload-generation command is produced or executed."
    )

    return result


# ---------------------------------------------------------
# KNOWLEDGE EXPORT
# ---------------------------------------------------------

def knowledge() -> Dict[str, Any]:
    return {
        "tool": TOOL_NAME,
        "display_name": TOOL_DISPLAY_NAME,
        "version": TOOL_VERSION,
        "owner": "HM INSAN ALI",
        "safe_mode": True,
        "execution_enabled": EXECUTION_ENABLED,
        "payload_generation_enabled": PAYLOAD_GENERATION_ENABLED,
        "target_execution_enabled": TARGET_EXECUTION_ENABLED,
        "types": PAYLOAD_TYPES,
        "command_modes": COMMAND_MODES,
        "connection_modes": CONNECTION_MODES,
        "payload_modes": PAYLOAD_MODES,
        "transports": TRANSPORTS,
        "special_modes": SPECIAL_MODES,
        "defaults": DEFAULTS,
        "capabilities": CAPABILITIES,
    }


def export_knowledge(
    output_path: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Export MSFPC knowledge to JSON.

    Default location:
    data/central_automation/tools/msfpc_knowledge.json
    """

    if output_path:
        path = Path(output_path)
    else:
        path = Path(__file__).resolve().parent / "msfpc_knowledge.json"

    path.parent.mkdir(parents=True, exist_ok=True)

    import json

    data = knowledge()

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
        "saved": True,
        "path": str(path),
        "tool": TOOL_NAME,
    }


# ---------------------------------------------------------
# SAFE RUN GUARD
# ---------------------------------------------------------

def run(*args: Any, authorized: bool = False, **kwargs: Any) -> Dict[str, Any]:
    """
    Deliberately blocked execution entry point.

    MSFPC creates executable payloads, so this adapter does not
    automate payload generation or target execution.
    """

    return {
        "ok": False,
        "blocked": True,
        "tool": TOOL_NAME,
        "reason": (
            "MSFPC execution is disabled in Tamanna safe mode. "
            "This adapter provides knowledge, classification, "
            "validation and analysis only."
        ),
        "authorized": authorized,
        "execution_enabled": EXECUTION_ENABLED,
        "payload_generation_enabled": PAYLOAD_GENERATION_ENABLED,
    }


# ---------------------------------------------------------
# TAMANNA BRIDGE FUNCTIONS
# ---------------------------------------------------------

def msfpc_status() -> Dict[str, Any]:
    return status()


def msfpc_help() -> Dict[str, Any]:
    return help_info()


def msfpc_classify(value: str) -> Dict[str, Any]:
    return classify(value)


def msfpc_match_capability(text: str) -> Dict[str, Any]:
    return match_capability(text)


def msfpc_analyze(**kwargs: Any) -> Dict[str, Any]:
    return analyze_request(**kwargs)


def msfpc_knowledge() -> Dict[str, Any]:
    return knowledge()


def msfpc_export_knowledge(
    output_path: Optional[str] = None,
) -> Dict[str, Any]:
    return export_knowledge(output_path)


def msfpc_run(
    *args: Any,
    authorized: bool = False,
    **kwargs: Any,
) -> Dict[str, Any]:
    return run(
        *args,
        authorized=authorized,
        **kwargs,
    )


# ---------------------------------------------------------
# SELF TEST
# ---------------------------------------------------------

def self_test() -> Dict[str, Any]:
    tests = {
        "status": status()["ok"],
        "help": help_info()["ok"],
        "type_windows": validate_type("windows").ok,
        "type_python": validate_type("python").ok,
        "port_443": validate_port(443).ok,
        "connection_reverse": validate_connection("reverse").ok,
        "staged": validate_payload_mode("staged").ok,
        "transport_https": validate_transport("https").ok,
        "capability_match": bool(
            match_capability(
                "understand staged reverse HTTPS payload type"
            )["matches"]
        ),
        "execution_blocked": run()["blocked"],
    }

    return {
        "ok": all(tests.values()),
        "tool": TOOL_NAME,
        "version": TOOL_VERSION,
        "tests": tests,
    }


if __name__ == "__main__":
    import json

    print(
        json.dumps(
            {
                "status": status(),
                "self_test": self_test(),
            },
            indent=2,
            ensure_ascii=False,
        )
    )
PY