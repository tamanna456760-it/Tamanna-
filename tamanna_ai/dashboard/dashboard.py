"""Dashboard utilities for status and metrics."""

from __future__ import annotations

from typing import Any, Dict


class Dashboard:
    def __init__(self):
        self.metrics: Dict[str, Any] = {"uptime": 0, "requests": 0}

    def update(self, **kwargs):
        self.metrics.update(kwargs)
        return self.metrics

    def view(self) -> Dict[str, Any]:
        return {"status": "ok", "metrics": self.metrics}


dashboard = Dashboard()

__all__ = ["Dashboard", "dashboard"]
