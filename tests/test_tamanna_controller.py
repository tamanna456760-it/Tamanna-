"""Unit tests for the Tamanna core controller."""

from tamanna_ai.brain.brain import KnowledgeBrain
from tamanna_ai.core.controller import TamannaController


def make_controller():
    return TamannaController(brain=KnowledgeBrain())


def test_rejects_non_string_message():
    result = make_controller().respond(None)
    assert result == {"ok": False, "reply": "Message must be text."}


def test_rejects_empty_message():
    result = make_controller().respond("   ")
    assert result == {"ok": False, "reply": "Please enter a message."}


def test_status_command_returns_system_information():
    result = make_controller().respond("SYSTEM STATUS")
    assert result["ok"] is True
    assert result["reply"] == "Tamanna AI: System status checked."
    assert result["power"]["status"] == "ONLINE"
    assert "python" in result["power"]


def test_remember_and_recall_are_available_in_injected_brain():
    controller = make_controller()
    saved = controller.respond("remember project audit")
    recalled = controller.respond("recall")

    assert saved["ok"] is True
    assert saved["memory_count"] == 1
    assert recalled["ok"] is True
    assert recalled["reply"] == "project audit"
    assert recalled["memory_count"] == 1


def test_remember_rejects_empty_item():
    result = make_controller().respond("remember   ")
    assert result == {"ok": False, "reply": "Tell me what to remember."}


def test_unknown_command_returns_brain_context_and_timestamp():
    result = make_controller().respond("hello Tamanna")
    assert result["ok"] is True
    assert result["input"] == "hello Tamanna"
    assert result["brain"]["prompt"] == "hello Tamanna"
    assert result["timestamp"]
    assert "need a knowledge source or AI model" in result["reply"]
