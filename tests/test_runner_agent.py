from pathlib import Path
from unittest.mock import patch

import pytest

from runner.python.agent import Agent, run


def test_run_never_invokes_a_shell():
    with patch("runner.python.agent.subprocess.run") as mocked:
        mocked.return_value.returncode = 0
        mocked.return_value.stdout = "ok"
        code, output = run(["python", "--version"])
    assert code == 0
    assert output == "ok"
    assert mocked.call_args.kwargs["shell"] is False


def test_agent_rejects_parent_traversal_stage_path(tmp_path):
    (tmp_path / ".git").mkdir()
    with pytest.raises(ValueError, match="safe relative paths"):
        Agent({
            "repo_path": str(tmp_path),
            "stage_paths": ["../outside.txt"],
            "lockfile": str(tmp_path / "lock"),
            "logfile": str(tmp_path / "agent.log"),
        })


def test_git_wrapper_accepts_argument_list(tmp_path):
    (tmp_path / ".git").mkdir()
    agent = Agent({
        "repo_path": str(tmp_path),
        "lockfile": str(tmp_path / "lock"),
        "logfile": str(tmp_path / "agent.log"),
    })
    with patch("runner.python.agent.run", return_value=(0, "ok")) as mocked:
        result = agent.git(["status", "--short"])
    assert result == (0, "ok")
    assert mocked.call_args.args[0] == ["git", "status", "--short"]


def test_agent_has_no_destructive_reset_or_whole_repo_staging():
    source = Path("runner/python/agent.py").read_text(encoding="utf-8")
    assert 'self.git("reset --hard' not in source
    assert 'self.git("add -A")' not in source
