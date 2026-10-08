"""Extension loader for optional plugins."""

from __future__ import annotations

from typing import Any, Dict, List


class ExtensionLoader:
    def __init__(self):
        self.extensions: Dict[str, Any] = {}

    def register(self, name: str, extension: Any) -> None:
        self.extensions[name] = extension

    def list(self) -> List[str]:
        return list(self.extensions.keys())


extension_loader = ExtensionLoader()

__all__ = ["ExtensionLoader", "extension_loader"]
