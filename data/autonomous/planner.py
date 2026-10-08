"""Autonomous planner stub."""

from __future__ import annotations


class AutonomousPlanner:
    def status(self):
        return {"status": "ok", "plans": []}

    def create_plan(self, brain_data):
        return {"status": "ok", "plan": [], "brain": brain_data}


autonomous_planner = AutonomousPlanner()

__all__ = ["AutonomousPlanner", "autonomous_planner"]
