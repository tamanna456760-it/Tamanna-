"""Regression tests for the public agent facade."""

from pathlib import Path

from tamanna_ai.agents import (
    AgentManager,
    BuilderAgent,
    CoderAgent,
    DeployerAgent,
    MonitorAgent,
    PlannerAgent,
    ReviewerAgent,
    TamannaAgents,
    TesterAgent,
)


def test_agent_package_exports_and_status(tmp_path):
    facade = TamannaAgents(str(tmp_path))
    status = facade.status()

    assert set(status["agents"]) == {
        "builder", "coder", "planner", "reviewer",
        "tester", "monitor", "deployer",
    }
    assert isinstance(facade.builder, BuilderAgent)
    assert isinstance(facade.coder, CoderAgent)
    assert isinstance(facade.planner, PlannerAgent)
    assert isinstance(facade.reviewer, ReviewerAgent)
    assert isinstance(facade.tester, TesterAgent)
    assert isinstance(facade.monitor, MonitorAgent)
    assert isinstance(facade.deployer, DeployerAgent)
    assert isinstance(AgentManager(), AgentManager)


def test_agent_facade_validates_python_inside_project(tmp_path):
    source = tmp_path / "sample.py"
    source.write_text("value = 1\n", encoding="utf-8")

    result = TamannaAgents(str(tmp_path)).validate_python("sample.py")
    assert result["success"] is True
    assert result["syntax"]["valid"] is True
    assert result["review"]["passed"] is True


def test_agent_facade_rejects_paths_outside_project(tmp_path):
    result = TamannaAgents(str(tmp_path)).validate_python("../outside.py")
    assert result["success"] is False
    assert "outside" in result["error"].lower()


def test_planner_requires_a_goal():
    result = PlannerAgent().create_plan("  ")
    assert result["success"] is False
    assert result["plan"] == []


def test_builder_does_not_overwrite_existing_files(tmp_path):
    target = Path(tmp_path) / "keep.txt"
    target.write_text("original", encoding="utf-8")

    result = BuilderAgent(tmp_path).create_file("keep.txt", "replacement")
    assert result["success"] is False
    assert target.read_text(encoding="utf-8") == "original"
