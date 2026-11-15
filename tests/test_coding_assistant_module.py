import asyncio

import pytest

from tamanna_ai.modules.coding_assistant import CodingAssistantModule


class FakeAssistant:
    async def generate_code(self, feature, **kwargs):
        return {"ok": True, "action": "generate", "feature": feature, "kwargs": kwargs}

    async def complete_code(self, code_prefix, **kwargs):
        return {"ok": True, "action": "complete", "code_prefix": code_prefix, "kwargs": kwargs}

    async def debug_code(self, error_report, **kwargs):
        return {"ok": True, "action": "debug", "error_report": error_report, "kwargs": kwargs}

    async def analyze_code(self, code, **kwargs):
        return {"ok": True, "action": kwargs["task"], "code": code, "kwargs": kwargs}


def test_generate_dispatches_to_existing_capability():
    result = asyncio.run(CodingAssistantModule(FakeAssistant()).execute(
        "generate", {"feature": "Build a calculator", "language": "Python"}
    ))
    assert result["ok"] is True
    assert result["action"] == "generate"
    assert result["feature"] == "Build a calculator"


def test_complete_and_debug_dispatch():
    module = CodingAssistantModule(FakeAssistant())
    completed = asyncio.run(module.execute("complete", {"code_prefix": "def add("}))
    debugged = asyncio.run(module.execute("debug", {"error_report": "ImportError"}))
    assert completed["action"] == "complete"
    assert debugged["action"] == "debug"


@pytest.mark.parametrize("action", ["explain", "review", "refactor"])
def test_analysis_actions_use_static_analysis_without_execution(action):
    result = asyncio.run(CodingAssistantModule(FakeAssistant()).execute(
        action, {"code": "print('hello')", "language": "Python"}
    ))
    assert result["ok"] is True
    assert result["kwargs"]["task"]


def test_unknown_action_and_missing_input_are_rejected():
    module = CodingAssistantModule(FakeAssistant())
    with pytest.raises(ValueError, match="Unsupported"):
        asyncio.run(module.execute("shell", {"command": "whoami"}))
    with pytest.raises(ValueError, match="feature is required"):
        asyncio.run(module.execute("generate", {}))


def test_oversized_source_is_rejected_before_model_call():
    module = CodingAssistantModule(FakeAssistant())
    with pytest.raises(ValueError, match="40000"):
        asyncio.run(module.execute("review", {"code": "x" * 40001}))
