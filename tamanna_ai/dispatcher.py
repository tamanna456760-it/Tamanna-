"""Dispatcher for sending tasks to AI subsystems."""

from __future__ import annotations

from typing import Any, Dict, List


class TamannaDispatcher:
    def __init__(self):
        self.routes: Dict[str, Any] = {}

    def register(self, name: str, handler: Any) -> None:
        self.routes[name] = handler

    def dispatch(self, name: str, payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
        handler = self.routes.get(name)
        if handler is None:
            return {"status": "not_found", "route": name, "payload": payload or {}}
        result = handler(payload or {}) if callable(handler) else handler
        return {"status": "ok", "route": name, "result": result}

    def list_routes(self) -> List[str]:
        return list(self.routes.keys())


dispatcher = TamannaDispatcher()

__all__ = ["TamannaDispatcher", "dispatcher"]
