#!/usr/bin/env python3
"""Explicit GitHub clone/update helper; no shell and no implicit directory changes."""
import subprocess
from pathlib import Path

from logger import log

GIT_REPO_URL = "https://github.com/tamanna456760-it/Tamanna-.git"
LOCAL_PATH = Path("./Tamanna-")


def git_setup():
    target = LOCAL_PATH.expanduser().resolve()
    if not target.exists():
        target.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(
            ["git", "clone", "--branch", "main", "--single-branch", GIT_REPO_URL, str(target)],
            check=True,
        )
        log("Git repo cloned on main")
        return target

    if not (target / ".git").exists():
        raise ValueError(f"Target exists but is not a Git repository: {target}")

    status = subprocess.run(
        ["git", "-C", str(target), "status", "--porcelain"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    if status.strip():
        raise RuntimeError("Refusing to pull over local changes; review or commit them first")

    branch = subprocess.run(
        ["git", "-C", str(target), "branch", "--show-current"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    if branch != "main":
        raise RuntimeError(f"Refusing to update branch {branch!r}; expected main")

    subprocess.run(
        ["git", "-C", str(target), "pull", "--ff-only", "origin", "main"],
        check=True,
    )
    log("Git repo updated on main")
    return target
