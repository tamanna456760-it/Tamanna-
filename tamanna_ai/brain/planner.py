"""Deterministic task-plan builder; creating a plan does not execute it."""
from typing import Any

def create_plan(goal: str, steps: list[str] | None = None) -> dict[str, Any]:
    clean_goal = str(goal).strip()
    if not clean_goal:
        raise ValueError("goal is required")
    if steps is None:
        steps = ["inspect requirements", "prepare a change plan", "implement", "run tests", "review results"]
    if not isinstance(steps, list):
        raise TypeError("steps must be a list")
    normalized = [str(step).strip() for step in steps]
    if any(not step for step in normalized):
        raise ValueError("plan steps cannot be empty")
    return {"goal": clean_goal, "status": "planned", "execution_started": False,
            "steps": [{"number": i + 1, "task": step, "status": "pending"} for i, step in enumerate(normalized)]}

__all__ = ["create_plan"]
