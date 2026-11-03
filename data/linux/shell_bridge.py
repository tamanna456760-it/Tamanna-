"""Restricted Linux diagnostics bridge.

This module intentionally exposes a small read-only command allowlist.
It never invokes a shell and does not accept pipelines or shell operators.
"""

from __future__ import annotations

import shlex
import subprocess
from pathlib import Path
from typing import Sequence


class ShellBridge:
    """Run bounded, read-only diagnostics inside the project directory."""

    MAX_TIMEOUT = 30
    MAX_OUTPUT = 12_000

    def __init__(self, root: str = "."):
        self.root = Path(root).resolve()

    def _parse(self, command: str) -> list[str]:
        if not isinstance(command, str) or not command.strip():
            raise ValueError("no command provided")
        if len(command) > 2_000 or any(ord(char) < 32 and char not in "\t" for char in command):
            raise ValueError("command contains invalid control characters or is too long")

        try:
            args = shlex.split(command, posix=True)
        except ValueError as exc:
            raise ValueError("command quoting is invalid") from exc

        if not args:
            raise ValueError("no command provided")

        executable = args[0]
        allowed: dict[str, set[tuple[str, ...]]] = {
            "pwd": {()},
            "whoami": {()},
            "date": {()},
            "uname": {("-a",)},
            "df": {("-h",)},
            "free": {("-h",)},
            "python": {("--version",)},
            "python3": {("--version",)},
            "ps": {("-eo", "pid,comm")},
            "git": {
                ("status", "--short"),
                ("log", "-5", "--oneline"),
                ("diff", "--stat"),
            },
        }

        if executable == "ls":
            options = []
            paths = []
            for item in args[1:]:
                if item.startswith("-"):
                    if any(char not in "lah" for char in item[1:]):
                        raise ValueError("unsupported ls option")
                    options.append(item)
                else:
                    paths.append(item)
            if len(paths) > 1:
                raise ValueError("ls accepts at most one path")
            if paths:
                target = (self.root / paths[0]).resolve()
                try:
                    target.relative_to(self.root)
                except ValueError as exc:
                    raise ValueError("path is outside the project directory") from exc
                if not target.exists():
                    raise ValueError("path does not exist")
                return ["ls", *options, str(target)]
            return ["ls", *options, str(self.root)]

        if executable not in allowed or tuple(args[1:]) not in allowed[executable]:
            raise ValueError("command is not in the read-only allowlist")

        return args

    def run(self, command: str, timeout: int = 15) -> dict:
        if isinstance(timeout, bool) or not isinstance(timeout, int):
            return {"ok": False, "error": "timeout must be an integer"}
        if not 1 <= timeout <= self.MAX_TIMEOUT:
            return {
                "ok": False,
                "error": f"timeout must be between 1 and {self.MAX_TIMEOUT} seconds",
            }

        try:
            args = self._parse(command)
        except ValueError as exc:
            return {"ok": False, "error": str(exc)}

        try:
            result = subprocess.run(
                args,
                cwd=self.root,
                shell=False,
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False,
            )
            return {
                "ok": result.returncode == 0,
                "command": command,
                "returncode": result.returncode,
                "stdout": result.stdout[-self.MAX_OUTPUT:],
                "stderr": result.stderr[-self.MAX_OUTPUT:],
            }
        except subprocess.TimeoutExpired:
            return {"ok": False, "error": "command timed out", "command": command}
        except OSError as exc:
            return {
                "ok": False,
                "error": f"command could not be started: {type(exc).__name__}",
                "command": command,
            }


shell_bridge = ShellBridge()

__all__ = ["ShellBridge", "shell_bridge"]
