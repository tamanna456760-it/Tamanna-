"""Planner for creating task steps."""

from __future__ import annotations

from typing import Any, Dict, List


class Planner:
    def __init__(self):
        self.tasks: List[str] = []

    def create_plan(self, task: str) -> Dict[str, Any]:
        steps = ["inspect", "implement", "verify"]
        self.tasks.append(task)
        return {"status": "ok", "task": task, "steps": steps}


planner = Planner()

__all__ = ["Planner", "planner"]
