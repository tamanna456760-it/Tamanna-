"""Runtime manager for local execution."""

from __future__ import annotations

from typing import Any, Dict


class RuntimeManager:
    def __init__(self):
        self.processes: Dict[str, Any] = {}

    def register(self, name: str, process: Any) -> None:
        self.processes[name] = process

    def list(self):
        return list(self.processes.keys())


runtime_manager = RuntimeManager()

__all__ = ["RuntimeManager", "runtime_manager"]
