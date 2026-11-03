"""Tests for the Linux tool manager's real, restricted execution behavior."""

from pathlib import Path

from data.linux.tool_manager import LinuxToolManager


def test_tool_manager_reports_supported_diagnostics(tmp_path: Path):
    manager = LinuxToolManager(str(tmp_path))

    assert "pwd" in manager.tools()
    assert "git status --short" in manager.tools()
    assert "cat" not in manager.tools()
    assert "rm" not in manager.tools()


def test_tool_manager_executes_real_diagnostic(tmp_path: Path):
    result = LinuxToolManager(str(tmp_path)).run("pwd")

    assert result["ok"] is True
    assert result["system"]
    assert Path(result["stdout"].strip()) == tmp_path.resolve()


def test_tool_manager_does_not_fake_success_for_blocked_command(tmp_path: Path):
    result = LinuxToolManager(str(tmp_path)).run("rm -rf /")

    assert result["ok"] is False
    assert "allowlist" in result["error"]
