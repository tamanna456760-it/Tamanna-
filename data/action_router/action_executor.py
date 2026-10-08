"""Action executor integration."""

from __future__ import annotations

from typing import Any, Dict


class ActionExecutor:
    def __init__(self):
        self._registry = {}

    def register(self, name: str, handler):
        self._registry[name] = handler
        return handler

    def run(self, name: str, *args, **kwargs):
        handler = self._registry.get(name)
        if handler is None:
            raise ValueError(f"No action registered: {name}")
        return handler(*args, **kwargs)


executor = ActionExecutor()

__all__ = ["ActionExecutor", "executor"]
