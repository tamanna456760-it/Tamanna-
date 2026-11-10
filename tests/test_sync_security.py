"""Regression tests for safe, explicit Tamanna Git synchronization."""
import sys
import unittest
from pathlib import Path
from unittest.mock import patch
from types import SimpleNamespace

REPO_ROOT = Path(__file__).resolve().parents[1]
RUNNER_PYTHON = REPO_ROOT / "runner" / "python"
sys.path.insert(0, str(RUNNER_PYTHON))

import auto_sync_monitor
import git_sync
import synce
import tamannna_master


class SafeSyncTests(unittest.TestCase):
    def test_git_sync_helper_denies_push_by_default(self):
        with self.assertRaises(PermissionError):
            git_sync.git_commit_push()

    def test_synce_rejects_parent_path(self):
        with self.assertRaises(ValueError):
            synce._safe_paths(["../secrets.env"])

    def test_all_sync_helpers_reject_repository_wide_path(self):
        with self.assertRaises(ValueError):
            synce._safe_paths(["."])
        with self.assertRaises(ValueError):
            auto_sync_monitor._safe_paths("./")
        with self.assertRaises(ValueError):
            tamannna_master._safe_sync_paths(["."])
        with self.assertRaises(ValueError):
            git_sync.git_commit_push(paths=["."], allow_push=True)

    def test_all_sync_helpers_reject_secret_paths(self):
        for secret_path in [".env", ".env.production", "config/credentials.json", "keys/server.pem", "api/token.txt"]:
            with self.subTest(path=secret_path):
                with self.assertRaises(ValueError):
                    synce._safe_paths([secret_path])
                with self.assertRaises(ValueError):
                    auto_sync_monitor._safe_paths(secret_path)
                with self.assertRaises(ValueError):
                    tamannna_master._safe_sync_paths([secret_path])
                with self.assertRaises(ValueError):
                    git_sync.git_commit_push(paths=[secret_path], allow_push=True)

    def test_sync_helpers_reject_glob_pathspecs(self):
        with self.assertRaises(ValueError):
            synce._safe_paths(["**/*"])
        with self.assertRaises(ValueError):
            auto_sync_monitor._safe_paths("*.py")

    def test_master_run_requires_argument_list(self):
        with self.assertRaises(ValueError):
            tamannna_master.run("echo unsafe")

    @patch("tamannna_master.subprocess.run")
    def test_master_run_does_not_enable_shell(self, mocked_run):
        mocked_run.return_value = SimpleNamespace(
            returncode=0, stdout="", stderr=""
        )
        tamannna_master.run(["printf", "%s", "safe;not-a-shell-command"])
        self.assertNotIn("shell", mocked_run.call_args.kwargs)
        self.assertEqual(
            mocked_run.call_args.args[0],
            ["printf", "%s", "safe;not-a-shell-command"],
        )

    def test_monitor_has_no_automatic_file_mover(self):
        self.assertFalse(hasattr(auto_sync_monitor, "move_file"))


if __name__ == "__main__":
    unittest.main()
