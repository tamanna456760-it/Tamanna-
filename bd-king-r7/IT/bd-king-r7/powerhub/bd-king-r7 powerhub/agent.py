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
import subprocess
import sys
import time
import uuid
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
    LOG.info("RUN: %s (cwd=%s)", cmd, cwd)
    p = subprocess.Popen(
        cmd,
        shell=True,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        executable="/bin/bash",
    )
    out_lines = []
    try:
        for line in p.stdout:
            out_lines.append(line.rstrip("\n"))
            LOG.debug(line.rstrip("\n"))
        p.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        p.kill()
        raise
    return p.returncode, "\n".join(out_lines)


class Agent:
    def __init__(self, cfg):
        self.repo_path = Path(cfg["repo_path"]).expanduser()
        self.branch = cfg.get("branch", "powerhub-auto")
        self.remote = cfg.get("remote", "origin")
        self.user = cfg.get("user") or os.environ.get("USER", "nobody")
        self.interval = int(cfg.get("interval_seconds", 60))
        self.push_changes = bool(cfg.get("push_changes", False))
        self.fix_cmds = cfg.get("fix_cmds", [])
        self.build_cmds = cfg.get("build_cmds", [])
        self.ficar = cfg.get("ficar", "ficar")
        self.powersync = cfg.get("power_sync", "power_sync")
        self.lockfile = Path(
            cfg.get("lockfile", "/var/lock/bd-king-r7-powerhub.lock"))
        self.logfile = Path(
            cfg.get("logfile", "/var/log/bd-king-r7-powerhub.log"))
        self.server_url = cfg.get("server_url", "").rstrip("/")
        self.agent_id = cfg.get("agent_id", str(uuid.uuid4()))
        self.auth_token = cfg.get("auth_token", "")
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
            r = requests.post(url, json=payload, headers=headers, timeout=15)
            self._write_log(f"POST {url} => {r.status_code}")
            return r.status_code, r.text
        except Exception as e:
            self._write_log(f"POST {url} failed: {e}")
            return None, str(e)

    def git(self, cmd, cwd=None, timeout=300):
        full = f"git {cmd}"
        rc, out = run(full, cwd=str(cwd or self.repo_path), timeout=timeout)
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
            # try reset to remote branch to avoid divergence
            rc, _ = self.git(
                f"ls-remote --exit-code {self.remote} {self.branch}")
            if rc == 0:
                self.git(f"reset --hard {self.remote}/{self.branch}")

            # pull latest
            self.git(f"pull --rebase {self.remote} {self.branch}")

            # run fixers
            fixer_out = []
            for cmd in self.fix_cmds:
                if not cmd:
                    continue
                rc, out = run(cmd, cwd=str(self.repo_path))
                fixer_out.append({"cmd": cmd, "rc": rc, "out": out})

            # stage all changes
            self.git("add -A")

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

            # update marker files
            uid = str(uuid.uuid4())
            self.repo_path.joinpath(self.ficar).write_text(
                f"Updated at: {now_iso()}\nUUID: {uid}\n"
            )
            self.repo_path.joinpath(self.powersync).write_text(
                f"Last run: {now_iso()} BUILD_OK={build_ok}\n"
            )
            self.git(f'add "{self.ficar}" "{self.powersync}" || true')

            changes_rc, changes_out = self.git("status --porcelain")
            has_changes = bool(changes_out.strip())

            commit_sha = None
            committed = False
            if has_changes and build_ok:
                commit_msg = f"Automated sync/fix/build {now_iso()}"
                self.git(f'commit -m "{commit_msg}" || true')
                committed = True
                # get last commit sha
                rc, out = self.git("rev-parse --short HEAD")
                if rc == 0:
                    commit_sha = out.strip()
                if self.push_changes:
                    # push (create upstream if not exists)
                    rc, out = self.git(
                        f"push -u {self.remote} {self.branch} || true")
                    self._write_log(f"push rc={rc}")
            elif has_changes and not build_ok:
                # reset staged changes so human can review
                self.git("reset --mixed || true")
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
