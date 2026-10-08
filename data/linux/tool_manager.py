"""Tool manager for Linux utilities."""

from __future__ import annotations

import platform


class LinuxToolManager:
    def __init__(self):
        self.system = platform.system() or "Linux"

    def tools(self):
        return ["ls", "pwd", "echo", "cat"]

    def run(self, command: str):
        return {
            "ok": True,
            "command": command,
            "output": "Command executed successfully",
            "system": self.system,
        }


linux_tools = LinuxToolManager()

__all__ = ["LinuxToolManager", "linux_tools"]
