"""Plugin manager."""

from __future__ import annotations

from typing import Any, Dict


class PluginManager:
    def __init__(self):
        self.plugins: Dict[str, Any] = {}

    def add(self, name: str, plugin: Any) -> None:
        self.plugins[name] = plugin

    def list(self):
        return list(self.plugins.keys())


plugin_manager = PluginManager()

__all__ = ["PluginManager", "plugin_manager"]
