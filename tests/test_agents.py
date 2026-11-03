"""Regression tests for Tamanna AI's local agents."""

from pathlib import Path

from tamanna_ai.agents.builder import BuilderAgent
from tamanna_ai.agents.coder import CoderAgent
from tamanna_ai.agents.deployer import DeployerAgent
from tamanna_ai.agents.monitor import MonitorAgent
from tamanna_ai.agents.planner import PlannerAgent
from tamanna_ai.agents.reviewer import ReviewerAgent
from tamanna_ai.agents.tester import TesterAgent


def test_builder_creates_file_without_overwriting(tmp_path: Path):
    agent = BuilderAgent(tmp_path)
    created = agent.create_file("src/example.py", "answer = 42\n")
    refused = agent.create_file("src/example.py", "answer = 0\n")

    assert created["success"] is True
    assert refused["status"] == "already_exists"
    assert (tmp_path / "src/example.py").read_text() == "answer = 42\n"


def test_builder_rejects_path_traversal(tmp_path: Path):
    agent = BuilderAgent(tmp_path)

    try:
        agent.create_file("../outside.py", "unsafe = True\n")
    except ValueError as exc:
        assert "outside" in str(exc).lower()
    else:
        raise AssertionError("Path traversal was not rejected")

    assert not (tmp_path.parent / "outside.py").exists()


def test_coder_reports_python_syntax_errors():
    result = CoderAgent().validate_python("def broken(:\n")

    assert result["valid"] is False
    assert result["line"] == 1


def test_reviewer_flags_dynamic_code_execution():
    result = ReviewerAgent().review_python("exec('print(1)')\n")

    assert result["passed"] is False
    assert any(item["severity"] == "high" for item in result["findings"])


def test_planner_rejects_empty_goal_and_creates_default_plan():
    agent = PlannerAgent()

    assert agent.create_plan(" ")["success"] is False
    result = agent.create_plan("Improve the test suite")

    assert result["success"] is True
    assert len(result["plan"]) >= 1
    assert all(item["status"] == "pending" for item in result["plan"])


def test_tester_validates_syntax_and_blocks_outside_test_path(tmp_path: Path):
    source = tmp_path / "valid.py"
    source.write_text("value = 1\n", encoding="utf-8")
    agent = TesterAgent()

    assert agent.validate_syntax(str(source))["success"] is True
    outside = agent.run_unittest(str(tmp_path), "../outside")

    assert outside["success"] is False
    assert "outside" in outside["error"].lower()


def test_monitor_reports_disk_usage_for_existing_directory(tmp_path: Path):
    result = MonitorAgent().check_disk(str(tmp_path))

    assert result["success"] is True
    assert result["total_bytes"] > 0
    assert 0 <= result["free_percent"] <= 100


def test_deployer_preflight_reports_missing_files(tmp_path: Path):
    result = DeployerAgent(tmp_path).preflight(
        required_files=["Main.py"],
        required_commands=[],
    )

    assert result["success"] is False
    assert result["status"] == "blocked"
    assert result["missing_files"] == ["Main.py"]
    assert result["deployment_executed"] is False
