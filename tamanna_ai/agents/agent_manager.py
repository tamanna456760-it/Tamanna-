"""Agent manager for coordinating autonomous workers."""

from __future__ import annotations

from typing import Any, Dict, List


class AgentManager:
    def __init__(self):
        self.agents: Dict[str, Dict[str, Any]] = {}

    def register(self, name: str, agent: Dict[str, Any]) -> None:
        self.agents[name] = agent

    def list_agents(self) -> List[str]:
        return list(self.agents.keys())

    def get(self, name: str) -> Dict[str, Any]:
        return self.agents.get(name, {"name": name, "status": "idle"})

    def run(self, name: str, payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
        agent = self.get(name)
        agent["status"] = "running"
        agent["last_payload"] = payload or {}
        return {"status": "ok", "agent": name, "result": agent}


agent_manager = AgentManager()

__all__ = ["AgentManager", "agent_manager"]
