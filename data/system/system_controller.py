"""Unified system controller."""

from __future__ import annotations


class TamannaSystemController:
    def overview(self):
        return {"status": "ok", "version": "1.0.0"}


tamanna_system = TamannaSystemController()

__all__ = ["TamannaSystemController", "tamanna_system"]
