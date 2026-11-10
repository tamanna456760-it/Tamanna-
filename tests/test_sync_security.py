"""Regression tests for safe, explicit Tamanna synchronization."""
import importlib.util
import os
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

REPO_ROOT = Path(__file__).resolve().parents[1]
RUNNER_PYTHON = REPO_ROOT / "runner" / "python"
sys.path.insert(0, str(RUNNER_PYTHON))

import auto_sync_monitor
import git_sync
import synce
import tamannna_master
import agent as powerhub_agent
import tamanna_sync
import tamanna_derive_sync
import enable_auto_sync
import tamanna_system


def load_sync_engine():
    path = RUNNER_PYTHON / "tamanna_bd-king-r7_sunc.py"
    spec = importlib.util.spec_from_file_location("tamanna_local_sync_engine", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


local_sync_engine = load_sync_engine()


class SafeSyncTests(unittest.TestCase):
    def test_git_sync_helper_denies_push_by_default(self):
        with self.assertRaises(PermissionError):
            git_sync.git_commit_push()

    def test_all_git_sync_helpers_reject_parent_and_broad_paths(self):
        cases = [
            (synce._safe_paths, ["../secrets.env"]),
            (synce._safe_paths, ["."]),
            (auto_sync_monitor._safe_paths, "*.py"),
            (tamannna_master._safe_sync_paths, ["."]),
            (git_sync.git_commit_push, ),
        ]
        for function, *args in cases[:-1]:
            with self.subTest(function=function.__module__):
                with self.assertRaises(ValueError):
                    function(*args)
        with self.assertRaises(ValueError):
            git_sync.git_commit_push(paths=["."], allow_push=True)

    def test_sync_helpers_reject_secret_paths(self):
        secret_paths = [
            ".env", ".env.production", "config/credentials.json",
            "keys/server.pem", "api/token.txt",
        ]
        for secret_path in secret_paths:
            with self.subTest(path=secret_path):
                for function, args in [
                    (synce._safe_paths, ([secret_path],)),
                    (auto_sync_monitor._safe_paths, (secret_path,)),
                    (tamannna_master._safe_sync_paths, ([secret_path],)),
                    (git_sync.git_commit_push, ()),
                    (powerhub_agent.safe_relative_paths, ([secret_path],)),
                ]:
                    with self.assertRaises(ValueError):
                        if function is git_sync.git_commit_push:
                            function(paths=[secret_path], allow_push=True)
                        else:
                            function(*args)

    def test_sync_helpers_reject_glob_pathspecs(self):
        with self.assertRaises(ValueError):
            synce._safe_paths(["**/*"])
        with self.assertRaises(ValueError):
            auto_sync_monitor._safe_paths("*.py")

    def test_master_run_requires_argument_list_and_uses_no_shell(self):
        with self.assertRaises(ValueError):
            tamannna_master.run("echo unsafe")
        with patch("tamannna_master.subprocess.run") as mocked_run:
            mocked_run.return_value = SimpleNamespace(returncode=0, stdout="", stderr="")
            tamannna_master.run(["printf", "%s", "safe;literal"])
            self.assertNotIn("shell", mocked_run.call_args.kwargs)
            self.assertEqual(
                mocked_run.call_args.args[0],
                ["printf", "%s", "safe;literal"],
            )

    def test_agent_rejects_shell_operators_and_command_strings(self):
        for command in [
            "echo ok && touch unsafe",
            "bash -c 'touch unsafe'",
            ["sh", "-c", "id"],
            ["echo", "|", "cat"],
        ]:
            with self.subTest(command=command):
                with self.assertRaises(ValueError):
                    powerhub_agent.command_args(command)

    def test_agent_refuses_dirty_worktree_before_pull(self):
        agent = object.__new__(powerhub_agent.Agent)
        agent.git = lambda *args, **kwargs: (0, " M app.py\\n")
        with self.assertRaisesRegex(RuntimeError, "Working tree is not clean"):
            agent.ensure_clean_checkout()

        agent.git = lambda *args, **kwargs: (0, "")
        self.assertIsNone(agent.ensure_clean_checkout())

    @patch("agent.subprocess.Popen")
    def test_agent_runs_without_a_shell(self, mocked_popen):
        mocked_popen.return_value = SimpleNamespace(
            communicate=lambda timeout=None: ("safe output", None),
            returncode=0,
        )
        rc, output = powerhub_agent.run(["printf", "%s", "literal;value"])
        self.assertEqual((rc, output), (0, "safe output"))
        self.assertIs(mocked_popen.call_args.kwargs["shell"], False)

    def test_drive_sync_is_disabled_by_default(self):
        with patch.dict(os.environ, {}, clear=True):
            self.assertEqual(tamanna_sync.sync_once(), 0)
            tamanna_derive_sync.main()

    def test_drive_sync_state_cannot_overwrite_credentials_or_use_symlink(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            upload = root / "uploads"
            upload.mkdir()
            credentials = root / "credentials.json"
            credentials.write_text("{}", encoding="utf-8")
            state = root / "state.json"

            self.assertEqual(
                tamanna_sync.validate_state_file(state, upload, credentials),
                state.resolve(),
            )
            with self.assertRaisesRegex(ValueError, "must not overwrite"):
                tamanna_sync.validate_state_file(credentials, upload, credentials)
            with self.assertRaisesRegex(ValueError, "symlink"):
                link = root / "state-link.json"
                try:
                    link.symlink_to(state)
                except (OSError, NotImplementedError):
                    self.skipTest("Symlinks are not supported on this runner")
                tamanna_sync.validate_state_file(link, upload, credentials)
            with self.assertRaisesRegex(ValueError, "outside the upload folder"):
                tamanna_sync.validate_state_file(upload / "state.json", upload, credentials)

    def test_drive_sync_rejects_credential_uploads(self):
        for name in [
            ".env", ".env.production", "credentials.json",
            "token.pickle", "service-account.json", "private.pem",
        ]:
            with self.subTest(name=name):
                self.assertFalse(tamanna_sync.is_safe_upload(Path("/tmp") / name))

    def test_local_mirror_rejects_secret_and_symlink_files(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            secret = root / ".env"
            secret.write_text("SECRET=value", encoding="utf-8")
            regular = root / "app.py"
            regular.write_text("print('ok')", encoding="utf-8")
            self.assertFalse(local_sync_engine.is_safe_file(secret))
            self.assertTrue(local_sync_engine.is_safe_file(regular))
            link = root / "linked.py"
            try:
                link.symlink_to(regular)
            except (OSError, NotImplementedError):
                self.skipTest("Symlinks are not supported on this runner")
            self.assertFalse(local_sync_engine.is_safe_file(link))

    def test_local_mirror_deletes_are_disabled_by_default(self):
        self.assertFalse(local_sync_engine.ALLOW_MIRROR_DELETE)

    def test_legacy_auto_sync_is_not_activated_by_default(self):
        with patch.dict(os.environ, {}, clear=True):
            enable_auto_sync.main()

    def test_system_ping_uses_shell_free_bounded_subprocess(self):
        with patch("tamanna_system.subprocess.run") as mocked_run:
            mocked_run.return_value = SimpleNamespace(returncode=0)
            self.assertTrue(tamanna_system.ping("example.com"))
            args, kwargs = mocked_run.call_args
            self.assertEqual(args[0][-1], "example.com")
            self.assertIs(kwargs["check"], False)
            self.assertEqual(kwargs["timeout"], 5)
            self.assertNotIn("shell", kwargs)

    def test_system_ping_rejects_whitespace_host(self):
        with patch("tamanna_system.subprocess.run") as mocked_run:
            self.assertFalse(tamanna_system.ping("example.com; touch /tmp/x"))
            mocked_run.assert_not_called()

    def test_monitor_has_no_automatic_file_mover(self):
        self.assertFalse(hasattr(auto_sync_monitor, "move_file"))


if __name__ == "__main__":
    unittest.main()
