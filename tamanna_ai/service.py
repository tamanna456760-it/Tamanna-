"""Service layer helpers for higher-level operations."""

from __future__ import annotations

from typing import Any, Dict


class TamannaService:
    def __init__(self):
        self.name = "TamannaService"

    def ping(self) -> Dict[str, Any]:
        return {"status": "ok", "service": self.name}

    def run(self, task: str, payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
        return {"status": "ok", "task": task, "payload": payload or {}}


service = TamannaService()

__all__ = ["TamannaService", "service"]
