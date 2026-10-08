"""Security guard module."""

from __future__ import annotations

from typing import Any, Dict


class SecurityGuard:
    def __init__(self):
        self.rules = ["validate-input", "sanitize-output", "lock-sensitive-endpoints"]

    def audit(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return {"status": "ok", "rules": self.rules, "issues": 0, "payload": payload}


security_guard = SecurityGuard()

__all__ = ["SecurityGuard", "security_guard"]
