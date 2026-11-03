"""Security regression tests for the restricted Linux diagnostics bridge."""

from pathlib import Path

from data.linux.shell_bridge import ShellBridge


def test_shell_bridge_runs_allowed_read_only_command(tmp_path: Path):
    result = ShellBridge(str(tmp_path)).run("pwd")

    assert result["ok"] is True
    assert Path(result["stdout"].strip()) == tmp_path.resolve()


def test_shell_bridge_rejects_shell_metacharacters(tmp_path: Path):
    result = ShellBridge(str(tmp_path)).run("pwd; touch injected.txt")

    assert result["ok"] is False
    assert "allowlist" in result["error"]
    assert not (tmp_path / "injected.txt").exists()


def test_shell_bridge_rejects_command_substitution(tmp_path: Path):
    result = ShellBridge(str(tmp_path)).run("pwd $(touch injected.txt)")

    assert result["ok"] is False
    assert not (tmp_path / "injected.txt").exists()


def test_shell_bridge_rejects_arbitrary_commands(tmp_path: Path):
    result = ShellBridge(str(tmp_path)).run("bash -c 'echo unsafe'")

    assert result["ok"] is False
    assert "allowlist" in result["error"]


def test_shell_bridge_restricts_ls_paths_to_project(tmp_path: Path):
    result = ShellBridge(str(tmp_path)).run("ls ../")

    assert result["ok"] is False
    assert "outside" in result["error"]


def test_shell_bridge_enforces_timeout_bounds(tmp_path: Path):
    assert ShellBridge(str(tmp_path)).run("pwd", timeout=0)["ok"] is False
    assert ShellBridge(str(tmp_path)).run("pwd", timeout=31)["ok"] is False


def test_shell_bridge_rejects_non_integer_timeout(tmp_path: Path):
    result = ShellBridge(str(tmp_path)).run("pwd", timeout=True)

    assert result["ok"] is False
    assert "integer" in result["error"]
