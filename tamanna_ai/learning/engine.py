"""Learning engine."""

from __future__ import annotations

from typing import Any, Dict, List


class LearningEngine:
    def __init__(self):
        self.history: List[str] = []

    def record(self, item: str) -> None:
        self.history.append(item)

    def get_history(self) -> List[str]:
        return self.history

    def train(self, item: str) -> Dict[str, Any]:
        self.record(item)
        return {"status": "ok", "item": item, "count": len(self.history)}


learning_engine = LearningEngine()

__all__ = ["LearningEngine", "learning_engine"]
