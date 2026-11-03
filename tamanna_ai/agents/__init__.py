"""Tamanna AI agent package and safe project-scoped orchestration facade."""
from pathlib import Path
from typing import Optional

from .agent_manager import AgentManager, agent_manager
from .builder import BuilderAgent
from .coder import CoderAgent
from .planner import PlannerAgent
from .reviewer import ReviewerAgent
from .tester import TesterAgent
from .monitor import MonitorAgent
from .deployer import DeployerAgent


class TamannaAgents:
    """Unified access to built-in agents with safe manager registrations.

    Read-only/planning operations are exposed through AgentManager. File writes
    and arbitrary test execution remain explicit operations, not auto-runnable
    manager actions.
    """

    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root).resolve()
        self.builder = BuilderAgent(self.project_root)
        self.coder = CoderAgent()
        self.planner = PlannerAgent()
        self.reviewer = ReviewerAgent()
        self.tester = TesterAgent()
        self.monitor = MonitorAgent()
        self.deployer = DeployerAgent(str(self.project_root))
        self.manager = AgentManager()
        self._register_safe_agents()

    def _resolve_project_path(self, file_path: str) -> Path:
        if not isinstance(file_path, str) or not file_path.strip():
            raise ValueError("A non-empty project-relative file path is required.")
        candidate = Path(file_path)
        if not candidate.is_absolute():
            candidate = self.project_root / candidate
        resolved = candidate.resolve()
        if resolved != self.project_root and self.project_root not in resolved.parents:
            raise ValueError("Path is outside the project directory.")
        return resolved

    def _register_safe_agents(self) -> None:
        self.manager.register(
            "planner",
            lambda payload: self.planner.create_plan(
                payload.get("goal", ""),
                payload.get("steps") or [],
            ),
        )
        self.manager.register(
            "coder.validate",
            lambda payload: self.coder.validate_python(payload.get("source", "")),
        )
        self.manager.register(
            "reviewer.review",
            lambda payload: self.reviewer.review_python(payload.get("source", "")),
        )
        self.manager.register(
            "tester.syntax",
            lambda payload: self.tester.validate_syntax(
                str(self._resolve_project_path(payload.get("file_path", "")))
            ),
        )
        self.manager.register(
            "monitor.disk",
            lambda _payload: self.monitor.check_disk(str(self.project_root)),
        )
        self.manager.register(
            "deployer.preflight",
            lambda payload: self.deployer.preflight(
                payload.get("required_files"),
                payload.get("required_commands"),
            ),
        )

    def run_agent(self, name: str, payload: Optional[dict] = None) -> dict:
        """Run a registered safe agent using a structured payload."""
        return self.manager.run(name, payload)

    def status(self) -> dict:
        """Report built-in agent availability and safe manager registrations."""
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
            "manager": {
                "registered": self.manager.list_agents(),
                "write_agents_auto_enabled": False,
                "arbitrary_test_execution_auto_enabled": False,
            },
        }

    def validate_python(self, file_path: str) -> dict:
        """Validate and review a Python file inside the project root only."""
        try:
            path = self._resolve_project_path(file_path)
        except ValueError as exc:
            return {"success": False, "error": str(exc), "syntax": None, "review": None}
        syntax = self.coder.validate_file(path)
        if not syntax.get("valid", False):
            return {"success": False, "syntax": syntax, "review": None}
        review = self.reviewer.review_file(str(path))
        return {"success": True, "syntax": syntax, "review": review}

    def plan_task(self, goal: str, steps: Optional[list] = None) -> dict:
        """Create a plan without executing its steps."""
        return self.planner.create_plan(goal, steps or [])

    def deployment_check(self) -> dict:
        """Check deployment prerequisites without deploying."""
        return self.deployer.preflight()


__all__ = [
    "AgentManager",
    "agent_manager",
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
