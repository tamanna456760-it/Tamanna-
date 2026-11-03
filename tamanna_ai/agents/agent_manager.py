"""Safe in-process manager for explicitly registered Tamanna agents."""
from __future__ import annotations

from threading import RLock
from typing import Any, Mapping, Optional
import re

_NAME = re.compile(r"^[A-Za-z][A-Za-z0-9_.-]{0,63}$")


class AgentManager:
    def __init__(self) -> None:
        self._agents: dict[str, Any] = {}
        self._status: dict[str, dict[str, Any]] = {}
        self._lock = RLock()

    @staticmethod
    def _valid_name(name: Any) -> bool:
        return isinstance(name, str) and bool(_NAME.fullmatch(name))

    @staticmethod
    def _runner(agent: Any):
        if callable(agent):
            return agent
        method = getattr(agent, "run", None)
        return method if callable(method) else None

    def register(self, name: str, agent: Any, *, replace: bool = False) -> None:
        if not self._valid_name(name):
            raise ValueError("Invalid agent name.")
        runner = self._runner(agent)
        if runner is None:
            raise TypeError("Agent must be callable or implement run(payload).")
        with self._lock:
            if name in self._agents and not replace:
                raise ValueError("Agent is already registered.")
            if self._status.get(name, {}).get("status") == "running":
                raise RuntimeError("Cannot replace a running agent.")
            self._agents[name] = runner
            self._status[name] = {
                "name": name, "status": "idle", "run_count": 0,
                "last_error": None,
            }

    def unregister(self, name: str) -> bool:
        with self._lock:
            if name not in self._agents:
                return False
            if self._status[name]["status"] == "running":
                return False
            del self._agents[name]
            del self._status[name]
            return True

    def list_agents(self) -> list[str]:
        with self._lock:
            return sorted(self._agents)

    def get(self, name: str) -> Optional[dict[str, Any]]:
        with self._lock:
            status = self._status.get(name)
            return dict(status) if status is not None else None

    def run(self, name: str, payload: Optional[Mapping[str, Any]] = None) -> dict[str, Any]:
        if not self._valid_name(name):
            return {"status": "error", "error": "Invalid agent name."}
        if payload is None:
            safe_payload = {}
        elif isinstance(payload, Mapping):
            safe_payload = dict(payload)
        else:
            return {"status": "error", "error": "Payload must be a mapping."}

        with self._lock:
            runner = self._agents.get(name)
            if runner is None:
                return {"status": "not_found", "agent": name}
            state = self._status[name]
            if state["status"] == "running":
                return {"status": "busy", "agent": name}
            state["status"] = "running"
            state["run_count"] += 1
            state["last_error"] = None

        try:
            result = runner(safe_payload)
        except Exception as exc:
            with self._lock:
                state["status"] = "failed"
                state["last_error"] = type(exc).__name__
            return {
                "status": "error", "agent": name,
                "error": "Agent execution failed.",
                "error_type": type(exc).__name__,
            }

        if hasattr(result, "__await__"):
            close = getattr(result, "close", None)
            if callable(close):
                close()
            with self._lock:
                state["status"] = "failed"
                state["last_error"] = "AsyncHandlerUnsupported"
            return {
                "status": "error", "agent": name,
                "error": "Async handlers require an async adapter.",
                "error_type": "AsyncHandlerUnsupported",
            }

        with self._lock:
            state["status"] = "succeeded"
            state["last_error"] = None
        return {"status": "ok", "agent": name, "result": result}


agent_manager = AgentManager()

__all__ = ["AgentManager", "agent_manager"]
