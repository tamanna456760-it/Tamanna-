"""Autonomous builder stub."""

from __future__ import annotations


class SafeBuilder:
    def build(self, plan):
        return {"status": "ok", "plan": plan, "built": False}


safe_builder = SafeBuilder()

__all__ = ["SafeBuilder", "safe_builder"]
