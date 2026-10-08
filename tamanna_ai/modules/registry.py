"""Module registry."""

from __future__ import annotations

from typing import Any, Dict


class ModuleRegistry:
    def __init__(self):
        self.registry: Dict[str, Any] = {}

    def register(self, name: str, module: Any) -> None:
        self.registry[name] = module

    def get(self, name: str, default: Any = None) -> Any:
        return self.registry.get(name, default)


module_registry = ModuleRegistry()

__all__ = ["ModuleRegistry", "module_registry"]
