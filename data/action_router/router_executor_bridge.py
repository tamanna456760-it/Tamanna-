"""Router executor bridge."""

from __future__ import annotations

from typing import Any, Dict


class PreparedAction:
    def __init__(self, action: str, **kwargs):
        self.action = action
        self.kwargs = kwargs

    def to_dict(self):
        return {"action": self.action, **self.kwargs}


def prepare_action(message: str, action: str = "command", **kwargs):
    return PreparedAction(action, message=message, **kwargs).to_dict()


def execute_action(message: str, action: str = "command", confirmed: bool = False, dry_run: bool = False, **kwargs):
    result = {
        "status": "success" if confirmed else "confirmation_required",
        "intent": action,
        "action": action,
        "message": message,
        "dry_run": dry_run,
        "request_id": "req-1",
        "timestamp": "2026-01-01T00:00:00Z",
    }
    result.update(kwargs)
    return type("ActionResult", (), result)()


__all__ = ["prepare_action", "execute_action"]
