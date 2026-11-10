#!/usr/bin/env python3
"""Read-only file monitor. It never moves files or pushes automatically."""
import argparse
import os
import subprocess
import time
from datetime import datetime
from pathlib import Path

WATCH_PATH = Path(".").resolve()
LOG_FILE = Path("auto_sync.log")
SCAN_INTERVAL = 60
IGNORE_DIRS = {".git", "__pycache__", "node_modules", ".venv", "venv"}


def log(message):
    line = f"[{datetime.now().isoformat(timespec='seconds')}] {message}"
    with LOG_FILE.open("a", encoding="utf-8") as handle:
        handle.write(line + "\n")
    print(line, flush=True)


def detect_type(filename):
    suffix = Path(filename).suffix.lower()
    return {
        ".py": "python",
        ".js": "node",
        ".sh": "shell",
        ".html": "html",
        ".json": "json",
    }.get(suffix)


def scan():
    """Return candidate files without moving, executing, or modifying them."""
    found = []
    for root, dirs, files in os.walk(WATCH_PATH):
        dirs[:] = [name for name in dirs if name not in IGNORE_DIRS]
        for filename in files:
            file_type = detect_type(filename)
            if file_type:
                found.append((Path(root) / filename, file_type))
    log(f"Read-only scan found {len(found)} candidate files")
    return found


def _safe_paths(raw_paths):
    paths = [item.strip() for item in raw_paths.split(",") if item.strip()]
    if not paths:
        raise ValueError("TAMANNA_SYNC_PATHS must list one or more relative paths")
    for item in paths:
        path = Path(item)
        if path.is_absolute() or ".." in path.parts:
            raise ValueError(f"Unsafe sync path: {item}")
    return [Path(item).as_posix() for item in paths]


def explicit_sync():
    """One-shot push; requires an explicit CLI flag and environment opt-in."""
    if os.environ.get("TAMANNA_ENABLE_GIT_PUSH") != "1":
        raise PermissionError("Set TAMANNA_ENABLE_GIT_PUSH=1 to authorize this one-shot push")
    paths = _safe_paths(os.environ.get("TAMANNA_SYNC_PATHS", ""))
    repo = WATCH_PATH
    branch = subprocess.run(
        ["git", "-C", str(repo), "branch", "--show-current"],
        check=True, capture_output=True, text=True,
    ).stdout.strip()
    if branch != "main":
        raise RuntimeError(f"Refusing to push from branch {branch!r}; only main is allowed")
    subprocess.run(["git", "-C", str(repo), "add", "--", *paths], check=True)
    changed = subprocess.run(
        ["git", "-C", str(repo), "diff", "--cached", "--quiet"], check=False
    )
    if changed.returncode == 0:
        log("No staged changes in the configured allowlist")
        return
    if changed.returncode != 1:
        raise RuntimeError("Unable to inspect staged changes")
    message = f"manual Tamanna sync {datetime.now().isoformat(timespec='seconds')}"
    subprocess.run(["git", "-C", str(repo), "commit", "-m", message], check=True)
    subprocess.run(["git", "-C", str(repo), "push", "origin", "main"], check=True)
    log("Explicit one-shot sync completed")


def main():
    parser = argparse.ArgumentParser(description="Read-only Tamanna file monitor")
    parser.add_argument("--watch", action="store_true", help="repeat read-only scans")
    parser.add_argument("--sync", action="store_true", help="explicit one-shot allowlisted push")
    parser.add_argument("--interval", type=int, default=SCAN_INTERVAL)
    args = parser.parse_args()
    if args.interval < 10:
        parser.error("--interval must be at least 10 seconds")
    if args.sync:
        explicit_sync()
        return
    while True:
        scan()
        if not args.watch:
            break
        time.sleep(args.interval)


if __name__ == "__main__":
    main()
