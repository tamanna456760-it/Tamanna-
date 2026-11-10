#!/usr/bin/env python3
"""Conservative BD-KING-R7 agent: shell-free commands and opt-in allowlisted sync."""
import logging
import os
import re
import shlex
import signal
import subprocess
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

import requests
import yaml

LOG = logging.getLogger("bdking_agent")
LOG.setLevel(logging.INFO)
if not LOG.handlers:
    LOG.addHandler(logging.StreamHandler(sys.stdout))

DEFAULT_CONFIG_PATH = "/etc/bdking/agent.yml"
SHELL_OPERATORS = {"|", "||", "&&", ";", ">", ">>", "<", "2>", "&"}


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def command_args(command):
    """Parse a configured command without ever invoking a shell."""
    if isinstance(command, str):
        args = shlex.split(command)
    elif isinstance(command, (list, tuple)):
        args = [str(item) for item in command]
    else:
        raise ValueError("Commands must be strings or argument lists")
    if not args or any(item in SHELL_OPERATORS for item in args):
        raise ValueError("Empty commands and shell operators are not allowed")
    return args


def safe_relative_paths(values):
    if not isinstance(values, list) or not values:
        raise ValueError("sync_paths must be a non-empty list of explicit relative paths")
    forbidden = {"credentials.json", "id_rsa", "id_ed25519", "token", "token.txt"}
    result = []
    for value in values:
        if not isinstance(value, str) or not value.strip():
            raise ValueError("sync_paths entries must be non-empty strings")
        path = Path(value)
        parts = path.parts
        if (
            path.is_absolute() or not parts or value.strip() in {".", "./"}
            or ".." in parts or value.startswith(":")
            or any(char in value for char in "*?[]")
            or any(part == ".env" or part.startswith(".env.") for part in parts)
            or any(part.lower() in forbidden for part in parts)
            or any(Path(part).suffix.lower() in {".pem", ".key", ".p12", ".pfx"} for part in parts)
        ):
            raise ValueError(f"Unsafe or overly broad sync path: {value}")
        result.append(path.as_posix())
    return result


def run(cmd, cwd=None, timeout=300):
    args = command_args(cmd)
    LOG.info("RUN: %s (cwd=%s)", args[0], cwd)
    process = subprocess.Popen(
        args,
        shell=False,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    try:
        output, _ = process.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        process.kill()
        process.communicate()
        raise
    if output:
        for line in output.splitlines():
            LOG.info("%s", line)
    return process.returncode, output or ""


class Agent:
    def __init__(self, cfg):
        if not isinstance(cfg, dict):
            raise ValueError("Agent configuration must be a YAML mapping")
        self.repo_path = Path(cfg["repo_path"]).expanduser().resolve()
        self.branch = cfg.get("branch", "main")
        self.remote = cfg.get("remote", "origin")
        if self.branch != "main":
            raise ValueError("This agent is restricted to the main branch")
        if not isinstance(self.remote, str) or not re.fullmatch(r"[A-Za-z0-9._-]{1,128}", self.remote):
            raise ValueError("remote must be a simple configured Git remote name")
        self.user = cfg.get("user") or os.environ.get("USER", "nobody")
        self.interval = int(cfg.get("interval_seconds", 60))
        if self.interval < 10:
            raise ValueError("interval_seconds must be at least 10")
        self.push_changes = cfg.get("push_changes") is True and cfg.get("allow_git_push") is True
        self.sync_paths = safe_relative_paths(cfg.get("sync_paths", [])) if self.push_changes else []
        commands_enabled = cfg.get("allow_commands") is True
        self.fix_cmds = cfg.get("fix_cmds", []) if commands_enabled else []
        self.build_cmds = cfg.get("build_cmds", []) if commands_enabled else []
        for command in self.fix_cmds + self.build_cmds:
            command_args(command)
        self.ficar = self._safe_marker(cfg.get("ficar", "ficar"))
        self.powersync = self._safe_marker(cfg.get("power_sync", "power_sync"))
        self.lockfile = Path(cfg.get("lockfile", "/var/lock/bd-king-r7-powerhub.lock"))
        self.logfile = Path(cfg.get("logfile", "/var/log/bd-king-r7-powerhub.log"))
        self.server_url = cfg.get("server_url", "").rstrip("/")
        self.agent_id = cfg.get("agent_id", str(uuid.uuid4()))
        self.auth_token = cfg.get("auth_token", "")
        if not (self.repo_path / ".git").exists():
            raise ValueError(f"Repo path {self.repo_path} is not a Git repository")

    @staticmethod
    def _safe_marker(value):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Marker filenames must be non-empty relative paths")
        path = Path(value)
        if path.is_absolute() or ".." in path.parts or value in {".", "./"}:
            raise ValueError(f"Unsafe marker path: {value}")
        return path.as_posix()

    def _write_log(self, msg):
        self.logfile.parent.mkdir(parents=True, exist_ok=True)
        with self.logfile.open("a", encoding="utf-8") as handle:
            handle.write(f"[{now_iso()}] {msg}\n")

    def acquire_lock(self):
        self.lockfile.parent.mkdir(parents=True, exist_ok=True)
        try:
            fd = os.open(str(self.lockfile), os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
            try:
                os.write(fd, str(os.getpid()).encode())
            finally:
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
        except OSError:
            LOG.exception("release_lock failed")

    def post_report(self, payload):
        if not self.server_url:
            return None
        headers = {"Content-Type": "application/json"}
        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
        try:
            response = requests.post(
                f"{self.server_url}/api/report", json=payload, headers=headers, timeout=15
            )
            self._write_log(f"Report returned HTTP {response.status_code}")
            return response.status_code, response.text
        except requests.RequestException as error:
            self._write_log(f"Report request failed: {error}")
            return None, str(error)

    def git(self, *args, timeout=300, check=False):
        rc, output = run(["git", *args], cwd=str(self.repo_path), timeout=timeout)
        if check and rc != 0:
            raise RuntimeError(f"Git command failed: git {args[0]}")
        return rc, output

    def perform_run(self):
        self._write_log("run start")
        if not self.acquire_lock():
            return
        try:
            rc, _ = self.git("status", "--porcelain", check=True)
            current_rc, current_branch = self.git("branch", "--show-current", check=True)
            if current_rc != 0 or current_branch.strip() != "main":
                raise RuntimeError("Agent will only run on the checked-out main branch")

            fetch_rc, _ = self.git("fetch", self.remote, check=False)
            if fetch_rc != 0:
                raise RuntimeError("Git fetch failed; stopping without modifying the checkout")
            pull_rc, _ = self.git("pull", "--rebase", self.remote, "main", check=False)
            if pull_rc != 0:
                raise RuntimeError("Git pull/rebase failed; stopping for manual review")

            fixer_out = []
            for command in self.fix_cmds:
                rc, output = run(command, cwd=str(self.repo_path))
                fixer_out.append({"command": command_args(command), "rc": rc, "output": output})
                if rc != 0:
                    raise RuntimeError("A configured fixer command failed")

            build_ok = True
            build_out = []
            for command in self.build_cmds:
                rc, output = run(command, cwd=str(self.repo_path))
                build_out.append({"command": command_args(command), "rc": rc, "output": output})
                if rc != 0:
                    build_ok = False
                    break

            uid = str(uuid.uuid4())
            (self.repo_path / self.ficar).write_text(
                f"Updated at: {now_iso()}\nUUID: {uid}\n", encoding="utf-8"
            )
            (self.repo_path / self.powersync).write_text(
                f"Last run: {now_iso()} BUILD_OK={build_ok}\n", encoding="utf-8"
            )

            committed = False
            commit_sha = None
            if build_ok and self.push_changes:
                self.git("add", "--", *self.sync_paths, check=True)
                staged_status, _ = self.git("diff", "--cached", "--quiet", check=False)
                if staged_status == 1:
                    commit_rc, _ = self.git(
                        "commit", "-m", f"Explicit agent sync {now_iso()}", check=False
                    )
                    if commit_rc != 0:
                        raise RuntimeError("Git commit failed")
                    committed = True
                    _, sha = self.git("rev-parse", "--short", "HEAD", check=True)
                    commit_sha = sha.strip()
                    push_rc, _ = self.git("push", "-u", self.remote, "main", check=False)
                    if push_rc != 0:
                        raise RuntimeError("Git push failed")
                elif staged_status != 0:
                    raise RuntimeError("Unable to inspect staged changes")

            _, status = self.git("status", "--porcelain", check=True)
            report = {
                "agent_id": self.agent_id,
                "timestamp": now_iso(),
                "repo_path": str(self.repo_path),
                "branch": "main",
                "fixer_out": fixer_out,
                "build_ok": build_ok,
                "build_out": build_out,
                "has_changes": bool(status.strip()),
                "committed": committed,
                "commit_sha": commit_sha,
                "push_enabled": self.push_changes,
            }
            self.post_report(report)
            self._write_log("run finished")
        except Exception as error:
            LOG.exception("perform_run failed")
            self._write_log(f"run error: {error}")
        finally:
            self.release_lock()

    def run_loop(self):
        self._write_log("agent starting main loop")
        stop = False

        def handle_signal(_signal, _frame):
            nonlocal stop
            stop = True

        signal.signal(signal.SIGINT, handle_signal)
        signal.signal(signal.SIGTERM, handle_signal)
        while not stop:
            self.perform_run()
            for _ in range(self.interval):
                if stop:
                    break
                time.sleep(1)
        self._write_log("agent exiting")


def load_config(path=DEFAULT_CONFIG_PATH):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Config file not found: {path}")
    with open(path, encoding="utf-8") as handle:
        config = yaml.safe_load(handle)
    if not isinstance(config, dict):
        raise ValueError("Agent config must be a YAML mapping")
    return config


def main():
    config = load_config()
    if config.get("enabled") is not True:
        LOG.info("Agent disabled: set enabled: true in /etc/bdking/agent.yml to start")
        return
    agent = Agent(config)
    agent.run_loop()


if __name__ == "__main__":
    main()
