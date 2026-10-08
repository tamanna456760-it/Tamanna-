"""Linux shell bridge."""

from __future__ import annotations

import subprocess


class ShellBridge:
    def __init__(self, root: str = "."):
        self.root = root

    def run(self, command: str, timeout: int = 15):
        if not command.strip():
            return {"ok": False, "error": "no command provided"}
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            return {
                "ok": result.returncode == 0,
                "command": command,
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
            }
        except Exception as exc:
            return {"ok": False, "error": str(exc), "command": command}


shell_bridge = ShellBridge()

__all__ = ["ShellBridge", "shell_bridge"]
