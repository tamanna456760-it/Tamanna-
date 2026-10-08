
#!/usr/bin/env python3
# ============================================================
# Tamanna AI — Gobuster Tool Adapter V1
# Owner: HM INSAN ALI
#
# Gobuster 3.8
# ============================================================

from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path
from typing import Any, Dict, Optional


PROJECT_ROOT = Path(
    os.environ.get(
        "TAMANNA_PROJECT_ROOT",
        "/home/tamanna/Desktop/TI tamanna",
    )
).resolve()

DATA_DIR = PROJECT_ROOT / "data" / "central_automation"

STATE_FILE = DATA_DIR / "gobuster_tool_state.json"
KNOWLEDGE_FILE = DATA_DIR / "gobuster_knowledge.json"


# ============================================================
# GOBUSTER COMMAND KNOWLEDGE
# ============================================================

GOBUSTER_COMMANDS: Dict[str, Dict[str, Any]] = {

    "dir": {
        "purpose": "Directory/file enumeration mode",
        "category": "web_content_discovery",
        "risk": "medium",
    },

    "vhost": {
        "purpose": "Virtual-host enumeration mode",
        "category": "virtual_host_discovery",
        "risk": "medium",
    },

    "dns": {
        "purpose": "DNS subdomain enumeration mode",
        "category": "dns_discovery",
        "risk": "medium",
    },

    "fuzz": {
        "purpose": (
            "Fuzz the FUZZ keyword in URL, "
            "headers and request body"
        ),
        "category": "web_fuzzing",
        "risk": "medium",
    },

    "tftp": {
        "purpose": "TFTP enumeration mode",
        "category": "tftp_discovery",
        "risk": "medium",
    },

    "s3": {
        "purpose": "AWS S3 bucket enumeration mode",
        "category": "cloud_storage_discovery",
        "risk": "medium",
    },

    "gcs": {
        "purpose": "Google Cloud Storage enumeration mode",
        "category": "cloud_storage_discovery",
        "risk": "medium",
    },

    "help": {
        "purpose": "Show Gobuster command help",
        "category": "information",
        "risk": "low",
    },
}


CAPABILITY_KEYWORDS = {

    "web_content_discovery": [
        "directory",
        "directories",
        "file",
        "files",
        "content discovery",
        "web paths",
    ],

    "virtual_host_discovery": [
        "vhost",
        "virtual host",
        "virtual-host",
        "host discovery",
    ],

    "dns_discovery": [
        "dns",
        "subdomain",
        "subdomains",
        "dns discovery",
    ],

    "web_fuzzing": [
        "fuzz",
        "fuzzing",
        "web fuzzing",
        "request fuzzing",
    ],

    "tftp_discovery": [
        "tftp",
        "tftp enumeration",
    ],

    "cloud_storage_discovery": [
        "s3",
        "aws bucket",
        "aws s3",
        "gcs",
        "google cloud storage",
        "cloud bucket",
    ],
}


class GobusterToolAdapter:

    def __init__(
        self,
        project_root: Path = PROJECT_ROOT,
        execution_enabled: bool = False,
    ) -> None:

        self.project_root = Path(
            project_root
        ).resolve()

        self.execution_enabled = bool(
            execution_enabled
        )

        DATA_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.binary = shutil.which(
            "gobuster"
        )

        self.state = {
            "tool": "gobuster",
            "version": "3.8",
            "online": self.binary is not None,
            "binary": self.binary,
            "execution_enabled": (
                self.execution_enabled
            ),
            "authorization_required": True,
            "source_modification": False,
            "project_root": str(
                self.project_root
            ),
            "commands_loaded": len(
                GOBUSTER_COMMANDS
            ),
        }

        self._save_json(
            STATE_FILE,
            self.state,
        )

    # ========================================================
    # JSON
    # ========================================================

    def _save_json(
        self,
        path: Path,
        data: Any,
    ) -> None:

        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        temp = path.with_suffix(
            path.suffix + ".tmp"
        )

        with temp.open(
            "w",
            encoding="utf-8",
        ) as fh:

            json.dump(
                data,
                fh,
                indent=2,
                ensure_ascii=False,
            )

            fh.write("\n")

        temp.replace(path)

    # ========================================================
    # STATUS
    # ========================================================

    def status(self) -> Dict[str, Any]:

        version_output = None

        if self.binary:

            try:

                proc = subprocess.run(
                    [
                        self.binary,
                        "--version",
                    ],
                    capture_output=True,
                    text=True,
                    timeout=10,
                    check=False,
                )

                version_output = (
                    proc.stdout.strip()
                    or proc.stderr.strip()
                )

            except Exception as exc:

                version_output = (
                    f"{type(exc).__name__}: {exc}"
                )

        return {
            **self.state,
            "status": (
                "ONLINE"
                if self.binary
                else "OFFLINE"
            ),
            "detected_version": version_output,
        }

    # ========================================================
    # HELP
    # ========================================================

    def help(
        self,
        command: Optional[str] = None,
    ) -> Dict[str, Any]:

        if not self.binary:

            return {
                "ok": False,
                "status": "GOBUSTER_NOT_FOUND",
            }

        command_args = [
            self.binary
        ]

        if command:

            if command not in GOBUSTER_COMMANDS:

                return {
                    "ok": False,
                    "status": "UNKNOWN_COMMAND",
                    "command": command,
                }

            command_args.append(
                command
            )

        command_args.append(
            "--help"
        )

        try:

            proc = subprocess.run(
                command_args,
                capture_output=True,
                text=True,
                timeout=20,
                check=False,
            )

            return {
                "ok": True,
                "command": command,
                "returncode": proc.returncode,
                "stdout": proc.stdout,
                "stderr": proc.stderr,
            }

        except Exception as exc:

            return {
                "ok": False,
                "status": "HELP_ERROR",
                "error": (
                    f"{type(exc).__name__}: {exc}"
                ),
            }

    # ========================================================
    # COMMAND INFORMATION
    # ========================================================

    def command_info(
        self,
        command: str,
    ) -> Dict[str, Any]:

        if command not in GOBUSTER_COMMANDS:

            return {
                "ok": False,
                "status": "UNKNOWN_COMMAND",
                "command": command,
            }

        return {
            "ok": True,
            "command": command,
            **GOBUSTER_COMMANDS[command],
        }

    # ========================================================
    # CAPABILITY MATCHING
    # ========================================================

    def match_capability(
        self,
        feature: str,
    ) -> Dict[str, Any]:

        if not isinstance(
            feature,
            str,
        ):

            return {
                "ok": False,
                "status": "INVALID_FEATURE",
            }

        query = feature.lower().strip()

        matched_categories = []

        for category, keywords in (
            CAPABILITY_KEYWORDS.items()
        ):

            if any(
                keyword in query
                for keyword in keywords
            ):

                matched_categories.append(
                    category
                )

        commands = []

        for command, info in (
            GOBUSTER_COMMANDS.items()
        ):

            if info.get("category") in (
                matched_categories
            ):

                commands.append(
                    {
                        "command": command,
                        **info,
                    }
                )

        return {
            "ok": True,
            "feature": feature,
            "matched_categories": (
                matched_categories
            ),
            "commands": commands,
        }

    # ========================================================
    # COMMAND PREPARATION
    # ========================================================

    def prepare(
        self,
        command: str,
        args: Optional[list[str]] = None,
    ) -> Dict[str, Any]:

        if command not in GOBUSTER_COMMANDS:

            return {
                "ok": False,
                "status": "UNKNOWN_COMMAND",
                "command": command,
            }

        safe_args = list(
            args or []
        )

        prepared = {
            "ok": True,
            "status": "COMMAND_PREPARED",
            "tool": "gobuster",
            "version": "3.8",
            "command": command,
            "args": safe_args,
            "argv": [
                self.binary or "gobuster",
                command,
                *safe_args,
            ],
            "execution_allowed": (
                self.execution_enabled
            ),
            "authorization_required": True,
            "source_modified": False,
        }

        return prepared

    # ========================================================
    # KNOWLEDGE EXPORT
    # ========================================================

    def export_knowledge(
        self,
    ) -> Dict[str, Any]:

        knowledge = {
            "tool": "gobuster",
            "version": "3.8",
            "owner": "HM INSAN ALI",
            "description": (
                "Directory, VHOST, DNS, fuzzing, "
                "TFTP and cloud-storage enumeration tool"
            ),
            "commands": GOBUSTER_COMMANDS,
            "capabilities": list(
                CAPABILITY_KEYWORDS.keys()
            ),
            "safety": {
                "execution_default": False,
                "authorization_required": True,
                "source_modification": False,
            },
        }

        self._save_json(
            KNOWLEDGE_FILE,
            knowledge,
        )

        return knowledge

    # ========================================================
    # EXECUTION
    # ========================================================

    def run(
        self,
        command_data: Dict[str, Any],
        authorized: bool = False,
        timeout: int = 300,
    ) -> Dict[str, Any]:

        argv = command_data.get(
            "argv"
        )

        if not isinstance(
            argv,
            list,
        ) or not argv:

            return {
                "ok": False,
                "status": "INVALID_COMMAND",
            }

        if not authorized:

            return {
                "ok": False,
                "status": "AUTHORIZATION_REQUIRED",
                "argv": argv,
            }

        if not self.execution_enabled:

            return {
                "ok": False,
                "status": "EXECUTION_DISABLED",
                "argv": argv,
            }

        if not self.binary:

            return {
                "ok": False,
                "status": "GOBUSTER_NOT_FOUND",
            }

        try:

            timeout_value = max(
                1,
                min(
                    int(timeout),
                    600,
                ),
            )

        except (
            TypeError,
            ValueError,
        ):

            timeout_value = 300

        try:

            proc = subprocess.run(
                argv,
                cwd=str(
                    self.project_root
                ),
                capture_output=True,
                text=True,
                timeout=timeout_value,
                check=False,
            )

            return {
                "ok": proc.returncode == 0,
                "status": (
                    "SUCCESS"
                    if proc.returncode == 0
                    else "GOBUSTER_ERROR"
                ),
                "argv": argv,
                "returncode": proc.returncode,
                "stdout": proc.stdout,
                "stderr": proc.stderr,
            }

        except subprocess.TimeoutExpired:

            return {
                "ok": False,
                "status": "TIMEOUT",
                "argv": argv,
                "timeout": timeout_value,
            }

        except Exception as exc:

            return {
                "ok": False,
                "status": "EXECUTION_ERROR",
                "argv": argv,
                "error": (
                    f"{type(exc).__name__}: {exc}"
                ),
            }


# ============================================================
# GLOBAL INSTANCE
# ============================================================

gobuster_tool = GobusterToolAdapter()


# ============================================================
# TAMANNA BRIDGE
# ============================================================

def gobuster_status():
    return gobuster_tool.status()


def gobuster_help(
    command: Optional[str] = None,
):
    return gobuster_tool.help(
        command
    )


def gobuster_command_info(
    command: str,
):
    return gobuster_tool.command_info(
        command
    )


def gobuster_match_capability(
    feature: str,
):
    return gobuster_tool.match_capability(
        feature
    )


def gobuster_prepare(
    command: str,
    args: Optional[list[str]] = None,
):
    return gobuster_tool.prepare(
        command,
        args,
    )


def gobuster_export_knowledge():
    return gobuster_tool.export_knowledge()


def gobuster_run(
    command_data,
    authorized: bool = False,
    timeout: int = 300,
):
    return gobuster_tool.run(
        command_data,
        authorized=authorized,
        timeout=timeout,
    )


# ============================================================
# TOOL METADATA
# ============================================================

TOOL_METADATA = {
    "name": "gobuster",
    "display_name": "Gobuster",
    "version": "3.8",
    "owner": "HM INSAN ALI",
    "adapter": (
        "data.central_automation.tools."
        "gobuster_tool_adapter"
    ),
    "commands": list(
        GOBUSTER_COMMANDS.keys()
    ),
    "execution_enabled": False,
    "authorization_required": True,
    "source_modification": False,
}


print(
    "[TAMANNA AI] Gobuster Tool Adapter V1: "
    + (
        "ONLINE"
        if gobuster_tool.binary
        else "OFFLINE"
    )
)

print(
    "[TAMANNA AI] Gobuster commands loaded:",
    len(GOBUSTER_COMMANDS),
)


if __name__ == "__main__":

    print(
        "\n=== GOBUSTER STATUS ==="
    )

    print(
        json.dumps(
            gobuster_status(),
            indent=2,
            ensure_ascii=False,
        )
    )

    print(
        "\n=== COMMANDS ==="
    )

    for name in GOBUSTER_COMMANDS:
        print(
            f"- {name}: "
            f"{GOBUSTER_COMMANDS[name]['purpose']}"
        )

    print(
        "\n=== CAPABILITY TEST ==="
    )

    tests = [
        "discover web directories",
        "find DNS subdomains",
        "fuzz a web request",
        "discover virtual hosts",
        "find AWS S3 buckets",
        "find Google Cloud Storage buckets",
    ]

    for feature in tests:

        print(
            f"\n{feature}"
        )

        print(
            json.dumps(
                gobuster_match_capability(
                    feature
                ),
                indent=2,
                ensure_ascii=False,
            )
        )

    print(
        "\n=== KNOWLEDGE EXPORT ==="
    )

    knowledge = (
        gobuster_export_knowledge()
    )

    print(
        "Commands:",
        len(
            knowledge["commands"]
        ),
    )

    print(
        "Knowledge file:",
        KNOWLEDGE_FILE,
    )

    print(
        "\n[TAMANNA AI] Gobuster Adapter Test Complete."
    )
PY