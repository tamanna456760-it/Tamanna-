#!/usr/bin/env python3
"""Safe, opt-in Git synchronization for the Tamanna repository.

Watching is read-only. A push requires both the explicit --sync flag and
allow_git_push=true plus a non-empty sync_paths allowlist in config.json.
"""
import argparse
import json
import subprocess
import time
from pathlib import Path


def log(message):
    print("[TAMANNA SYNC] " + str(message), flush=True)


def load_config(config_path="config.json"):
    path = Path(config_path)
    if not path.is_file():
        raise FileNotFoundError(f"Configuration file not found: {path}")
    with path.open("r", encoding="utf-8") as handle:
        config = json.load(handle)
    if not isinstance(config, dict):
        raise ValueError("config.json must contain a JSON object")
    return config


def _safe_paths(values):
    if not isinstance(values, list) or not values:
        raise ValueError("sync_paths must be a non-empty list of relative paths")
    result = []
    for value in values:
        if not isinstance(value, str) or not value.strip():
            raise ValueError("sync_paths entries must be non-empty strings")
        path = Path(value)
        if path.is_absolute() or ".." in path.parts:
            raise ValueError(f"Unsafe sync path: {value}")
        result.append(path.as_posix())
    return result


def git_sync(repo, msg, *, allow_push=False, paths=None):
    """Commit only allowlisted paths; never push unless explicitly enabled."""
    if not allow_push:
        raise PermissionError("Git push is disabled; set allow_git_push=true and pass --sync")
    repo_path = Path(repo).expanduser().resolve()
    if not repo_path.is_dir():
        raise FileNotFoundError(f"Repository directory not found: {repo_path}")
    allowed_paths = _safe_paths(paths)

    root = subprocess.run(
        ["git", "-C", str(repo_path), "rev-parse", "--show-toplevel"],
        check=True, capture_output=True, text=True,
    ).stdout.strip()
    if Path(root).resolve() != repo_path:
        raise ValueError("git_repo must point to the repository root")

    branch = subprocess.run(
        ["git", "-C", str(repo_path), "branch", "--show-current"],
        check=True, capture_output=True, text=True,
    ).stdout.strip()
    if branch != "main":
        raise RuntimeError(f"Refusing to push from branch {branch!r}; only main is allowed")

    subprocess.run(
        ["git", "-C", str(repo_path), "add", "--", *allowed_paths],
        check=True,
    )
    staged = subprocess.run(
        ["git", "-C", str(repo_path), "diff", "--cached", "--quiet"],
        check=False,
    )
    if staged.returncode == 0:
        log("No staged changes in the configured allowlist")
        return False
    if staged.returncode != 1:
        raise RuntimeError("Unable to inspect staged changes")

    subprocess.run(
        ["git", "-C", str(repo_path), "commit", "-m", msg],
        check=True,
    )
    subprocess.run(
        ["git", "-C", str(repo_path), "push", "origin", "main"],
        check=True,
    )
    log("Explicit sync completed")
    return True


def report_status(repo):
    result = subprocess.run(
        ["git", "-C", str(Path(repo).expanduser().resolve()), "status", "--short"],
        check=True, capture_output=True, text=True,
    )
    log(result.stdout.rstrip() or "Working tree clean")


def main():
    parser = argparse.ArgumentParser(description="Read-only monitor; opt-in Git sync")
    parser.add_argument("--config", default="config.json")
    parser.add_argument("--watch", action="store_true", help="repeat read-only status checks")
    parser.add_argument("--sync", action="store_true", help="explicitly commit/push configured paths")
    args = parser.parse_args()

    config = load_config(args.config)
    repo = config.get("git_repo", ".")
    if args.sync:
        if config.get("allow_git_push") is not True:
            raise PermissionError("Set allow_git_push=true in config.json to enable explicit sync")
        message = str(config.get("auto_commit_message", "Manual Tamanna sync")).strip()
        if not message:
            raise ValueError("auto_commit_message cannot be empty")
        git_sync(repo, message, allow_push=True, paths=config.get("sync_paths"))
        return

    interval = config.get("scan_interval_sec", 60)
    if not isinstance(interval, int) or interval < 10:
        raise ValueError("scan_interval_sec must be an integer of at least 10 seconds")
    while True:
        report_status(repo)
        if not args.watch:
            break
        time.sleep(interval)


if __name__ == "__main__":
    main()
