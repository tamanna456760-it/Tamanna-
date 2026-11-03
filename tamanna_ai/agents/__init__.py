"""Unified public interface for Tamanna AI agents."""

from pathlib import Path
from typing import Optional

from .agent_manager import AgentManager
from .builder import BuilderAgent
from .coder import CoderAgent
from .deployer import DeployerAgent
from .monitor import MonitorAgent
from .planner import PlannerAgent
from .reviewer import ReviewerAgent
from .tester import TesterAgent


class TamannaAgents:
    """Coordinate the seven built-in project agents."""

    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root).resolve()
        self.builder = BuilderAgent(self.project_root)
        self.coder = CoderAgent()
        self.planner = PlannerAgent()
        self.reviewer = ReviewerAgent()
        self.tester = TesterAgent()
        self.monitor = MonitorAgent()
        self.deployer = DeployerAgent(str(self.project_root))

    def status(self) -> dict:
        return {
            "system": "Tamanna AI",
            "project_root": str(self.project_root),
            "agents": {
                "builder": True,
                "coder": True,
                "planner": True,
                "reviewer": True,
                "tester": True,
                "monitor": True,
                "deployer": True,
            },
        }

    def validate_python(self, file_path: str) -> dict:
        path = Path(file_path)
        if not path.is_absolute():
            path = self.project_root / path

        syntax = self.coder.validate_file(path)
        if not syntax.get("valid", False):
            return {"success": False, "syntax": syntax, "review": None}

        review = self.reviewer.review_file(str(path))
        return {
            "success": bool(review.get("passed", False)),
            "syntax": syntax,
            "review": review,
        }

    def plan_task(self, goal: str, steps: Optional[list] = None) -> dict:
        return self.planner.create_plan(goal, steps or [])

    def deployment_check(self) -> dict:
        return self.deployer.preflight()


__all__ = [
    "AgentManager",
    "BuilderAgent",
    "CoderAgent",
    "PlannerAgent",
    "ReviewerAgent",
    "TesterAgent",
    "MonitorAgent",
    "DeployerAgent",
    "TamannaAgents",
]
