"""Lightweight registry for Tamanna capability modules."""

from __future__ import annotations

from typing import Any


class ModuleRegistry:
    """Store named module objects and expose stable discovery methods."""

    def __init__(self) -> None:
        self.registry: dict[str, Any] = {}

    def register(self, name: str, module: Any) -> None:
        if not isinstance(name, str) or not name.strip():
            raise ValueError("Module name must be a non-empty string")
        self.registry[name.strip()] = module

    def get(self, name: str, default: Any = None) -> Any:
        return self.registry.get(name, default)

    def list(self) -> list[Any]:
        """Return registered modules in registration order."""
        return list(self.registry.values())

    def names(self) -> list[str]:
        """Return registered module names in registration order."""
        return list(self.registry.keys())


module_registry = ModuleRegistry()

__all__ = ["ModuleRegistry", "module_registry"]
