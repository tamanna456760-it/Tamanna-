"""Tamanna AI Planner Agent."""
from typing import Iterable
class PlannerAgent:
    def create_plan(self, goal: str, steps: Iterable[str] = ()) -> dict:
        goal = goal.strip()
        if not goal:
            return {
                "success": False,
                "error": "A goal is required.",
                "plan": [],
            }
        cleaned_steps = [
            step.strip()
            for step in steps
            if isinstance(step, str) and step.strip()
        ]
        if not cleaned_steps:
            cleaned_steps = [
                "Inspect the existing project and requirements.",
                "Identify files and dependencies involved.",
                "Prepare the smallest safe implementation.",
                "Run relevant tests and validation.",
                "Review the results before accepting changes.",
            ]
        return {
            "success": True,
            "goal": goal,
            "plan": [
                {"step": index, "task": task, "status": "pending"}
                for index, task in enumerate(cleaned_steps, start=1)
            ],
        }
if __name__ == "__main__":
    agent = PlannerAgent()
    print(agent.create_plan("Validate the Tamanna AI project"))