"""Read-only Linux diagnostic tool manager."""

from __future__ import annotations

import platform

from data.linux.shell_bridge import ShellBridge


class LinuxToolManager:
    """Expose only commands supported by the restricted shell bridge."""

    def __init__(self, root: str = "."):
        self.system = platform.system() or "Linux"
        self.bridge = ShellBridge(root)

    def tools(self):
        return [
            "pwd",
            "ls",
            "whoami",
            "date",
            "uname -a",
            "df -h",
            "free -h",
            "ps -eo pid,comm",
            "python --version",
            "python3 --version",
            "git status --short",
            "git log -5 --oneline",
            "git diff --stat",
        ]

    def run(self, command: str):
        result = self.bridge.run(command)
        return {
            **result,
            "system": self.system,
        }


linux_tools = LinuxToolManager()

__all__ = ["LinuxToolManager", "linux_tools"]
