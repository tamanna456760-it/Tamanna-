"""Agent subsystem package."""

from .agent_manager import AgentManager

__all__ = ["AgentManager"]
"""Tamanna AI Agents Package.
Provides a unified interface for the seven Tamanna AI agents.
"""
from pathlib import Path
from typing import Optional
from .builder import BuilderAgent
from .coder import CoderAgent
from .planner import PlannerAgent
from .reviewer import ReviewerAgent
from .tester import TesterAgent
from .monitor import MonitorAgent
from .deployer import DeployerAgent
class TamannaAgents:
    """Unified access to Tamanna AI agents."""
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
        """Report which agent interfaces are available."""
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
        """Validate Python syntax and return a code review."""
        path = Path(file_path)
        if not path.is_absolute():
            path = self.project_root / path
        syntax = self.coder.validate_file(path)
        if not syntax.get("valid", False):
            return {
                "success": False,
                "syntax": syntax,
                "review": None,
            }
        review = self.reviewer.review_file(str(path))
        return {
            "success": True,
            "syntax": syntax,
            "review": review,
        }
    def plan_task(self, goal: str, steps: Optional[list] = None) -> dict:
        """Create a plan without executing its steps."""
        return self.planner.create_plan(goal, steps or [])
    def deployment_check(self) -> dict:
        """Check deployment prerequisites without deploying."""
        return self.deployer.preflight()
__all__ = [
    "BuilderAgent",
    "CoderAgent",
    "PlannerAgent",
    "ReviewerAgent",
    "TesterAgent",
    "MonitorAgent",
    "DeployerAgent",
    "TamannaAgents",
]
if __name__ == "__main__":
    agents = TamannaAgents()
    print(agents.status())