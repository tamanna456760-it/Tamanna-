"""Security training helper."""

from __future__ import annotations

from typing import Any, Dict, List


class SecurityTrainer:
    def __init__(self):
        self.training_data: List[str] = []

    def add_case(self, case: str) -> None:
        self.training_data.append(case)

    def summarize(self) -> Dict[str, Any]:
        return {"status": "ok", "cases": len(self.training_data)}


security_trainer = SecurityTrainer()

__all__ = ["SecurityTrainer", "security_trainer"]
