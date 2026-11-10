#!/usr/bin/env python3
"""Explicit, allowlisted Git sync helper. Push is disabled unless opted in."""
import subprocess
from pathlib import Path


def git_commit_push(repo_path=".", paths=None, message="Manual Tamanna sync", *, allow_push=False):
    if not allow_push:
        raise PermissionError("Git push is disabled; pass allow_push=True explicitly")
    if not isinstance(paths, (list, tuple)) or not paths:
        raise ValueError("Provide a non-empty allowlist of relative paths")

    safe_paths = []
    for value in paths:
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Sync paths must be non-empty strings")
        path = Path(value)
        parts = path.parts
        forbidden_names = {"credentials.json", "id_rsa", "id_ed25519", "token", "token.txt"}
        if (
            path.is_absolute()
            or not parts
            or value.strip() in {".", "./"}
            or ".." in parts
            or value.startswith(":")
            or any(char in value for char in "*?[]")
            or any(part == ".env" or part.startswith(".env.") for part in parts)
            or any(part.lower() in forbidden_names for part in parts)
            or any(Path(part).suffix.lower() in {".pem", ".key", ".p12", ".pfx"} for part in parts)
        ):
            raise ValueError(f"Unsafe or overly broad sync path: {value}")
        safe_paths.append(path.as_posix())

    repo = Path(repo_path).expanduser().resolve()
    if not repo.is_dir():
        raise FileNotFoundError(f"Repository not found: {repo}")

    def git(*args, check=True):
        return subprocess.run(
            ["git", "-C", str(repo), *args],
            check=check, capture_output=True, text=True,
        )

    root = Path(git("rev-parse", "--show-toplevel").stdout.strip()).resolve()
    if root != repo:
        raise ValueError("repo_path must be the repository root")
    branch = git("branch", "--show-current").stdout.strip()
    if branch != "main":
        raise RuntimeError(f"Refusing to push from branch {branch!r}; only main is allowed")

    git("add", "--", *safe_paths)
    staged = git("diff", "--cached", "--quiet", check=False)
    if staged.returncode == 0:
        print("[TAMANNA SYNC] No staged changes in the configured allowlist")
        return False
    if staged.returncode != 1:
        raise RuntimeError("Unable to inspect staged changes")

    git("commit", "-m", message)
    git("push", "origin", "main")
    print("[TAMANNA SYNC] Explicit Git push completed")
    return True
