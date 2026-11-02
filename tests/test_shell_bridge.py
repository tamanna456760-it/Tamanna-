"""Security tests for the restricted shell bridge."""

from data.linux.shell_bridge import ShellBridge


def test_shell_bridge_rejects_shell_operators(tmp_path):
    bridge = ShellBridge(str(tmp_path))
    result = bridge.run("pwd && whoami")
    assert result["ok"] is False


def test_shell_bridge_rejects_arbitrary_commands(tmp_path):
    bridge = ShellBridge(str(tmp_path))
    result = bridge.run("python -c 'print(1)'")
    assert result["ok"] is False


def test_shell_bridge_allows_read_only_pwd(tmp_path):
    bridge = ShellBridge(str(tmp_path))
    result = bridge.run("pwd")
    assert result["ok"] is True
    assert result["stdout"].strip() == str(tmp_path.resolve())


def test_shell_bridge_rejects_paths_outside_project(tmp_path):
    bridge = ShellBridge(str(tmp_path))
    result = bridge.run("ls ../")
    assert result["ok"] is False
