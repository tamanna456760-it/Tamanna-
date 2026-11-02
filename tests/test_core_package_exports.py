"""Verify stable public imports for core and tool packages."""

from tamanna_ai.core import TamannaController, tamanna_controller
from tamanna_ai.tools import power_status, tamanna_echo


def test_core_controller_exports():
    assert isinstance(tamanna_controller, TamannaController)
    assert isinstance(TamannaController(), TamannaController)


def test_tool_exports():
    assert tamanna_echo("ready") == "Tamanna AI: ready"
    status = power_status()
    assert status["name"] == "Tamanna AI"
    assert status["status"] == "ONLINE"
