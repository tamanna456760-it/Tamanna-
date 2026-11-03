"""Regression tests for AgentManager."""
import pytest

from tamanna_ai.agents import AgentManager as ExportedAgentManager
from tamanna_ai.agents import agent_manager as shared_agent_manager
from tamanna_ai.agents.agent_manager import AgentManager


def test_public_package_exports_manager():
    assert ExportedAgentManager is AgentManager
    assert isinstance(shared_agent_manager, AgentManager)


def test_register_and_run_callable():
    manager = AgentManager()
    manager.register("echo", lambda payload: {"echo": payload["message"]})
    result = manager.run("echo", {"message": "hello"})
    assert result == {"status": "ok", "agent": "echo", "result": {"echo": "hello"}}
    assert manager.get("echo") == {
        "name": "echo", "status": "succeeded", "run_count": 1, "last_error": None
    }


def test_register_and_run_object_method():
    class ExampleAgent:
        def run(self, payload):
            return {"received": dict(payload)}

    manager = AgentManager()
    manager.register("example", ExampleAgent())
    assert manager.run("example", {"x": 1})["result"] == {"received": {"x": 1}}


def test_invalid_names_and_non_executable_agents_are_rejected():
    manager = AgentManager()
    with pytest.raises(ValueError):
        manager.register("../unsafe", lambda payload: payload)
    with pytest.raises(TypeError):
        manager.register("metadata-only", {"status": "idle"})


def test_duplicate_registration_requires_replace_flag():
    manager = AgentManager()
    manager.register("worker", lambda payload: "first")
    with pytest.raises(ValueError):
        manager.register("worker", lambda payload: "second")
    manager.register("worker", lambda payload: "second", replace=True)
    assert manager.run("worker")["result"] == "second"


def test_missing_agent_and_invalid_payload():
    manager = AgentManager()
    assert manager.run("missing") == {"status": "not_found", "agent": "missing"}
    manager.register("worker", lambda payload: payload)
    assert manager.run("worker", ["not", "a", "mapping"])["status"] == "error"


def test_handler_exception_does_not_leak_exception_message():
    def fail(_payload):
        raise RuntimeError("private internal detail")

    manager = AgentManager()
    manager.register("worker", fail)
    result = manager.run("worker")
    assert result["status"] == "error"
    assert result["error_type"] == "RuntimeError"
    assert "private internal detail" not in str(result)
    assert manager.get("worker")["status"] == "failed"


def test_unregister_and_sorted_agent_list():
    manager = AgentManager()
    manager.register("zeta", lambda payload: None)
    manager.register("alpha", lambda payload: None)
    assert manager.list_agents() == ["alpha", "zeta"]
    assert manager.unregister("zeta") is True
    assert manager.unregister("zeta") is False


def test_async_handler_is_not_reported_as_success():
    async def async_handler(_payload):
        return "done"

    manager = AgentManager()
    manager.register("async-worker", async_handler)
    result = manager.run("async-worker")
    assert result["status"] == "error"
    assert result["error_type"] == "AsyncHandlerUnsupported"
