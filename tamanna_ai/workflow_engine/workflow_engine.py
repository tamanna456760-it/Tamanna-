"""Workflow execution engine."""

from __future__ import annotations

from typing import Any, Dict, List


class WorkflowEngine:
    def __init__(self):
        self.steps: List[str] = []

    def add_step(self, name: str) -> None:
        self.steps.append(name)

    def run(self, name: str | None = None) -> Dict[str, Any]:
        if name:
            self.steps.append(name)
        return {"status": "ok", "steps": self.steps}


workflow_engine = WorkflowEngine()

__all__ = ["WorkflowEngine", "workflow_engine"]
