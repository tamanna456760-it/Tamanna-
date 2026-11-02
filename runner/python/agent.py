#!/usr/bin/env python3
"""
bd-king-r7 powerhub agent

- Reads /etc/bdking/agent.yml for configuration
- Every interval:
  - Pulls repo, switches/creates automation branch
  - Runs fixers and build/test commands
  - Updates 'ficar' and 'power_sync' marker files
  - Commits and optionally pushes changes
  - Posts a JSON report to orchestration server
- Uses lockfile to avoid overlapping runs
"""
import logging
import os
import signal
import shlex
import subprocess
import sys
import time
import uuid
import re
from datetime import datetime
from pathlib import Path

import requests
import yaml

LOG = logging.getLogger("bdking_agent")
LOG.setLevel(logging.INFO)
LOG.addHandler(logging.StreamHandler(sys.stdout))

DEFAULT_CONFIG_PATH = "/etc/bdking/agent.yml"


def now_iso():
    return datetime.utcnow().isoformat() + "Z"


def run(cmd, cwd=None, timeout=None):
    """Run a command as argv; never invoke a shell."""
    argv = shlex.split(cmd) if isinstance(cmd, str) else list(cmd)
    if not argv:
        return 2, "empty command"
    LOG.info("RUN: %s (cwd=%s)", argv[0], cwd)
    try:
        result = subprocess.run(
            argv, cwd=cwd, stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT, text=True,
            timeout=timeout or 300, shell=False, check=False,
        )
        return result.returncode, result.stdout
    except subprocess.TimeoutExpired:
        return 124, "command timed out"
    except OSError as exc:
        return 127, type(exc).__name__


class Agent:
    def __init__(self, cfg):
        self.repo_path = Path(cfg["repo_path"]).expanduser()
        self.branch = str(cfg.get("branch", "powerhub-auto"))
        self.remote = str(cfg.get("remote", "origin"))
        if not re.fullmatch(r"[A-Za-z0-9._/-]{1,120}", self.branch) or self.branch.startswith("-") or ".." in self.branch:
            raise ValueError("Invalid automation branch name")
        if not re.fullmatch(r"[A-Za-z0-9._-]{1,80}", self.remote) or self.remote.startswith("-"):
            raise ValueError("Invalid git remote name")
        self.user = cfg.get("user") or os.environ.get("USER", "nobody")
        self.interval = int(cfg.get("interval_seconds", 60))
        self.push_changes = bool(cfg.get("push_changes", False))
        self.fix_cmds = cfg.get("fix_cmds", [])
        self.build_cmds = cfg.get("build_cmds", [])
        # Only explicitly configured relative paths may be staged.
        self.stage_paths = cfg.get("stage_paths", [])
        if not isinstance(self.stage_paths, list):
            raise ValueError("stage_paths must be a list")
        for item in self.stage_paths:
            candidate = Path(str(item))
            if candidate.is_absolute() or ".." in candidate.parts or not str(item).strip():
                raise ValueError("stage_paths entries must be safe relative paths")
        self.lockfile = Path(
            cfg.get("lockfile", "/var/lock/bd-king-r7-powerhub.lock"))
        self.logfile = Path(
            cfg.get("logfile", "/var/log/bd-king-r7-powerhub.log"))
        self.server_url = cfg.get("server_url", "").rstrip("/")
        self.agent_id = cfg.get("agent_id", str(uuid.uuid4()))
        self.auth_token = os.environ.get("TAMANNA_AGENT_AUTH_TOKEN", "")
        if self.server_url and not (self.server_url.startswith("https://") or self.server_url.startswith("http://127.0.0.1") or self.server_url.startswith("http://localhost")):
            raise ValueError("Agent report URL must use HTTPS except for localhost")
        # ensure repo exists
        if not (self.repo_path / ".git").exists():
            LOG.error("Repo path %s is not a git repository", self.repo_path)
            raise SystemExit(1)

    def _write_log(self, msg):
        ts = now_iso()
        with open(self.logfile, "a") as f:
            f.write(f"[{ts}] {msg}\n")

    def acquire_lock(self):
        # simple lockfile existence + writing PID (works across reboots)
        try:
            fd = os.open(str(self.lockfile), os.O_CREAT |
                         os.O_EXCL | os.O_WRONLY)
            os.write(fd, str(os.getpid()).encode())
            os.close(fd)
            self._write_log("acquired lock")
            return True
        except FileExistsError:
            self._write_log("lock exists, skipping run")
            return False

    def release_lock(self):
        try:
            if self.lockfile.exists():
                self.lockfile.unlink()
                self._write_log("released lock")
        except Exception as e:
            LOG.exception("release_lock failed: %s", e)

    def post_report(self, payload):
        if not self.server_url:
            return
        headers = {"Content-Type": "application/json"}
        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
        url = f"{self.server_url}/api/report"
        try:
            r = requests.post(url, json=payload, headers=headers, timeout=15, allow_redirects=False)
            self._write_log(f"POST {url} => {r.status_code}")
            return r.status_code, r.text
        except Exception as e:
            self._write_log(f"POST {url} failed: {e}")
            return None, str(e)

    def git(self, cmd, cwd=None, timeout=300):
        args = list(cmd) if isinstance(cmd, (list, tuple)) else shlex.split(cmd)
        rc, out = run(["git", *args], cwd=str(cwd or self.repo_path), timeout=timeout)
        return rc, out

    def perform_run(self):
        self._write_log("run start")
        if not self.acquire_lock():
            return
        try:
            rc, out = self.git("fetch --all --prune")
            self._write_log(f"git fetch rc={rc}")
            # checkout or create branch
            rc, out = self.git(f"rev-parse --verify {self.branch}")
            if rc == 0:
                rc, out = self.git(f"checkout {self.branch}")
            else:
                # try create from remote main or from HEAD
                rc_main, _ = self.git(
                    f"ls-remote --exit-code {self.remote} main")
                if rc_main == 0:
                    rc, out = self.git(
                        f"checkout -b {self.branch} {self.remote}/main")
                else:
                    rc, out = self.git(f"checkout -b {self.branch}")
            self._write_log("checked out branch")
            # Never reset --hard or pull/rebase automatically: preserve local and
            # operator changes for review instead of overwriting the worktree.

            # run fixers
            fixer_out = []
            for cmd in self.fix_cmds:
                if not cmd:
                    continue
                rc, out = run(cmd, cwd=str(self.repo_path))
                fixer_out.append({"cmd": cmd, "rc": rc, "out": out})

            # Stage only operator-approved paths; never stage the entire repository.
            for item in self.stage_paths:
                self.git(["add", "--", item])

            # run build/test
            build_ok = True
            build_out = []
            for cmd in self.build_cmds:
                if not cmd:
                    continue
                rc, out = run(cmd, cwd=str(self.repo_path))
                build_out.append({"cmd": cmd, "rc": rc, "out": out})
                if rc != 0:
                    build_ok = False
                    break

            # Do not create or stage marker files at arbitrary configured paths.
            # Status and results are reported to the orchestrator instead.

            changes_rc, changes_out = self.git("status --porcelain")
            has_changes = bool(changes_out.strip())

            commit_sha = None
            committed = False
            if has_changes and build_ok:
                commit_msg = f"Automated sync/fix/build {now_iso()}"
                commit_rc, commit_out = run(["git", "commit", "-m", commit_msg], cwd=str(self.repo_path), timeout=60)
                committed = commit_rc == 0
                if not committed:
                    self._write_log(f"commit failed rc={commit_rc}")
                # get last commit sha only after a successful commit
                rc, out = self.git("rev-parse --short HEAD")
                if committed and rc == 0:
                    commit_sha = out.strip()
                if committed and self.push_changes:
                    # push (create upstream if not exists)
                    rc, out = run(["git", "push", "-u", self.remote, self.branch], cwd=str(self.repo_path), timeout=300)
                    self._write_log(f"push rc={rc}")
            elif has_changes and not build_ok:
                # reset staged changes so human can review
                self.git("reset --mixed")
            # prepare report
            report = {
                "agent_id": self.agent_id,
                "timestamp": now_iso(),
                "repo_path": str(self.repo_path),
                "branch": self.branch,
                "fixer_out": fixer_out,
                "build_ok": build_ok,
                "build_out": build_out,
                "has_changes": has_changes,
                "committed": committed,
                "commit_sha": commit_sha,
            }
            # post to orchestrator
            self.post_report(report)
            self._write_log("run finished")
        except Exception as e:
            LOG.exception("perform_run failed: %s", e)
            self._write_log(f"run error: {e}")
        finally:
            self.release_lock()

    def run_loop(self):
        self._write_log("agent starting main loop")
        # signal handling
        stop = False

        def _sig(_s, _f):
            nonlocal stop
            stop = True

        signal.signal(signal.SIGINT, _sig)
        signal.signal(signal.SIGTERM, _sig)

        while not stop:
            try:
                self.perform_run()
            except Exception:
                LOG.exception("error during perform_run")
            for _ in range(int(self.interval)):
                if stop:
                    break
                time.sleep(1)
        self._write_log("agent exiting")


def load_config(path=DEFAULT_CONFIG_PATH):
    if not os.path.exists(path):
        LOG.error("Config file not found: %s", path)
        raise SystemExit(1)
    with open(path) as f:
        return yaml.safe_load(f)


def main():
    cfg = load_config()
    agent = Agent(cfg)
    agent.run_loop()


if __name__ == "__main__":
    main()
