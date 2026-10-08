"""Report generation helper."""

from __future__ import annotations

from typing import Any, Dict, List


class ReportGenerator:
    def __init__(self):
        self.reports: List[Dict[str, Any]] = []

    def add(self, name: str, data: Dict[str, Any]) -> None:
        self.reports.append({"name": name, "data": data})

    def generate(self) -> List[Dict[str, Any]]:
        return self.reports


report_generator = ReportGenerator()

__all__ = ["ReportGenerator", "report_generator"]
