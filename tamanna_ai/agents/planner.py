"""Validated, deterministic task planning for Tamanna AI."""
from __future__ import annotations

from collections.abc import Sequence
from typing import Any, Optional


class PlannerAgent:
    """Create bounded plans without executing tasks or modifying project files."""

    DEFAULT_STEPS = (
        "Inspect the existing project and requirements.",
        "Identify files and dependencies involved.",
        "Prepare the smallest safe implementation.",
        "Run relevant tests and validation.",
        "Review the results before accepting changes.",
    )
    MAX_GOAL_LENGTH = 1000
    MAX_STEPS = 20
    MAX_STEP_LENGTH = 300

    @staticmethod
    def _error(message: str) -> dict[str, Any]:
        return {"success": False, "error": message, "plan": []}

    def create_plan(
        self,
        goal: str,
        steps: Optional[Sequence[str]] = None,
    ) -> dict[str, Any]:
        """Validate input and return a pending plan; never execute its tasks."""
        if not isinstance(goal, str):
            return self._error("Goal must be text.")
        normalized_goal = goal.strip()
        if not normalized_goal:
            return self._error("A goal is required.")
        if len(normalized_goal) > self.MAX_GOAL_LENGTH:
            return self._error(
                f"Goal must be at most {self.MAX_GOAL_LENGTH} characters."
            )

        if steps is None or steps == [] or steps == ():
            cleaned_steps = list(self.DEFAULT_STEPS)
        else:
            if isinstance(steps, (str, bytes, bytearray, dict)) or not isinstance(
                steps, Sequence
            ):
                return self._error("Steps must be a list or tuple of text items.")
            if len(steps) > self.MAX_STEPS:
                return self._error(f"A plan may contain at most {self.MAX_STEPS} steps.")

            cleaned_steps = []
            for index, step in enumerate(steps, start=1):
                if not isinstance(step, str):
                    return self._error(f"Step {index} must be text.")
                task = step.strip()
                if not task:
                    return self._error(f"Step {index} cannot be empty.")
                if len(task) > self.MAX_STEP_LENGTH:
                    return self._error(
                        f"Step {index} must be at most {self.MAX_STEP_LENGTH} characters."
                    )
                cleaned_steps.append(task)

        return {
            "success": True,
            "goal": normalized_goal,
            "step_count": len(cleaned_steps),
            "plan": [
                {"step": index, "task": task, "status": "pending"}
                for index, task in enumerate(cleaned_steps, start=1)
            ],
        }


if __name__ == "__main__":
    print(PlannerAgent().create_plan("Validate the Tamanna AI project"))
