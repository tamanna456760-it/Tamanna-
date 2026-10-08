"""Workflow loader."""

from __future__ import annotations

from typing import Any, Dict, List


class WorkflowLoader:
    def __init__(self):
        self.workflows: Dict[str, Any] = {}

    def register(self, name: str, workflow: Any) -> None:
        self.workflows[name] = workflow

    def names(self) -> List[str]:
        return list(self.workflows.keys())


workflow_loader = WorkflowLoader()

__all__ = ["WorkflowLoader", "workflow_loader"]
