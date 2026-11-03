"""Tests for bounded and validated task planning."""
import pytest

from tamanna_ai.agents.planner import PlannerAgent


@pytest.fixture
def planner():
    return PlannerAgent()


def test_creates_default_plan_for_goal(planner):
    result = planner.create_plan("  Upgrade Tamanna AI  ")
    assert result["success"] is True
    assert result["goal"] == "Upgrade Tamanna AI"
    assert result["step_count"] == 5
    assert [item["step"] for item in result["plan"]] == [1, 2, 3, 4, 5]
    assert all(item["status"] == "pending" for item in result["plan"])


def test_creates_plan_from_custom_steps(planner):
    result = planner.create_plan("Fix tests", [" Inspect ", "Run tests"])
    assert result["success"] is True
    assert [item["task"] for item in result["plan"]] == ["Inspect", "Run tests"]


@pytest.mark.parametrize("goal", [None, 1, [], {}])
def test_rejects_non_text_goal(planner, goal):
    result = planner.create_plan(goal)
    assert result["success"] is False
    assert result["error"] == "Goal must be text."
    assert result["plan"] == []


@pytest.mark.parametrize("goal", ["", "   "])
def test_rejects_empty_goal(planner, goal):
    assert planner.create_plan(goal)["error"] == "A goal is required."


def test_rejects_oversized_goal(planner):
    result = planner.create_plan("x" * (planner.MAX_GOAL_LENGTH + 1))
    assert result["success"] is False
    assert "at most" in result["error"]


@pytest.mark.parametrize("steps", ["abc", b"abc", {"one": "step"}, 42])
def test_rejects_non_sequence_steps(planner, steps):
    result = planner.create_plan("Goal", steps)
    assert result["success"] is False
    assert result["error"] == "Steps must be a list or tuple of text items."


def test_rejects_non_text_step(planner):
    result = planner.create_plan("Goal", ["valid", 12])
    assert result["success"] is False
    assert result["error"] == "Step 2 must be text."


def test_rejects_blank_step(planner):
    result = planner.create_plan("Goal", ["valid", "  "])
    assert result["success"] is False
    assert result["error"] == "Step 2 cannot be empty."


def test_rejects_too_many_steps(planner):
    result = planner.create_plan("Goal", ["step"] * (planner.MAX_STEPS + 1))
    assert result["success"] is False
    assert "at most" in result["error"]


def test_rejects_oversized_step(planner):
    result = planner.create_plan("Goal", ["x" * (planner.MAX_STEP_LENGTH + 1)])
    assert result["success"] is False
    assert "at most" in result["error"]


def test_empty_steps_use_safe_defaults(planner):
    assert planner.create_plan("Goal", [])["step_count"] == 5
    assert planner.create_plan("Goal", ())["step_count"] == 5


def test_planning_does_not_execute_or_mutate_tasks(planner):
    steps = ["Review code", "Run tests"]
    result = planner.create_plan("Goal", steps)
    assert result["success"] is True
    assert steps == ["Review code", "Run tests"]
    assert all(item["status"] == "pending" for item in result["plan"])
