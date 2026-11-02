"""Regression tests for Tamanna's core conversation controller."""

from tamanna_ai.core.controller import TamannaController


def test_empty_message_is_rejected():
    result = TamannaController().respond("   ")
    assert result["ok"] is False
    assert "enter a message" in result["reply"].lower()


def test_status_command_returns_power_status():
    result = TamannaController().respond("status")
    assert result["ok"] is True
    assert result["power"]["name"] == "Tamanna AI"
    assert result["power"]["status"] == "ONLINE"


def test_remember_and_recall_are_session_scoped():
    controller = TamannaController()
    saved = controller.respond("remember deploy only after approval")
    recalled = controller.respond("recall")

    assert saved["ok"] is True
    assert saved["memory_count"] == 1
    assert recalled["ok"] is True
    assert "deploy only after approval" in recalled["reply"]


def test_regular_message_returns_brain_context():
    result = TamannaController().respond("Explain the project")
    assert result["ok"] is True
    assert result["input"] == "Explain the project"
    assert result["brain"]["status"] == "ok"
