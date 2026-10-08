"""Base plugin interface."""

from __future__ import annotations

from typing import Any, Dict


class BasePlugin:
    name = "base"

    def run(self, payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
        return {"status": "ok", "plugin": self.name, "payload": payload or {}}


__all__ = ["BasePlugin"]
