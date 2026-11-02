"""Restricted, non-shell Linux command bridge.

Only read-only inspection commands are allowed. Arbitrary shell execution is
intentionally disabled; privileged mutations belong in separately reviewed
and authenticated application operations.
"""

from __future__ import annotations

import shlex
import subprocess
from pathlib import Path


class ShellBridge:
    ALLOWED_SIMPLE = {"pwd", "whoami", "uname", "ls"}
    ALLOWED_GIT = {"status", "log", "diff"}

    def __init__(self, root: str = "."):
        self.root = Path(root).resolve()

    def _safe_path(self, value: str) -> Path:
        candidate = (self.root / value).resolve()
        try:
            candidate.relative_to(self.root)
        except ValueError as exc:
            raise ValueError("path must stay inside the project root") from exc
        return candidate

    def run(self, command: str, timeout: int = 10):
        if not isinstance(command, str) or not command.strip():
            return {"ok": False, "error": "no command provided"}
        if timeout < 1 or timeout > 15:
            return {"ok": False, "error": "timeout must be between 1 and 15 seconds"}

        try:
            args = shlex.split(command)
            if not args:
                return {"ok": False, "error": "no command provided"}

            executable = args[0]
            if executable in self.ALLOWED_SIMPLE:
                if executable in {"pwd", "whoami", "uname"} and len(args) != 1:
                    return {"ok": False, "error": "arguments are not allowed for this command"}
                if executable == "ls":
                    if len(args) > 2 or any(arg.startswith("-") for arg in args[1:]):
                        return {"ok": False, "error": "ls accepts at most one relative path"}
                    target = self._safe_path(args[1] if len(args) == 2 else ".")
                    argv = ["ls", "--", str(target)]
                elif executable == "pwd":
                    argv = ["pwd"]
                elif executable == "whoami":
                    argv = ["whoami"]
                else:
                    argv = ["uname"]
            elif executable == "git":
                if len(args) < 2 or args[1] not in self.ALLOWED_GIT:
                    return {"ok": False, "error": "only git status, git log, and git diff are allowed"}
                if any(token in args[2:] for token in (";", "&&", "||", "|", ">", "<", "$(", "`")):
                    return {"ok": False, "error": "shell operators are not allowed"}
                argv = ["git", "-C", str(self.root), *args[1:]]
            else:
                return {
                    "ok": False,
                    "error": "command is not in the read-only allow-list",
                    "allowed": sorted(self.ALLOWED_SIMPLE) + ["git status", "git log", "git diff"],
                }

            result = subprocess.run(
                argv,
                cwd=str(self.root),
                shell=False,
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False,
            )
            return {
                "ok": result.returncode == 0,
                "command": executable,
                "returncode": result.returncode,
                "stdout": result.stdout[-12000:],
                "stderr": result.stderr[-4000:],
            }
        except (ValueError, OSError, subprocess.TimeoutExpired) as exc:
            return {"ok": False, "error": type(exc).__name__}


shell_bridge = ShellBridge()

__all__ = ["ShellBridge", "shell_bridge"]
