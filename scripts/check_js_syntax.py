#!/usr/bin/env python3
"""Parse-check tracked JavaScript files without executing application code."""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXCLUDED_PARTS = {
    ".git", "node_modules", ".venv", "venv", "dist", "build",
    "coverage", "__pycache__",
}


def tracked_javascript_files() -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files", "-z", "--", "*.js"],
        cwd=ROOT,
        check=True,
        stdout=subprocess.PIPE,
    )
    paths = [
        ROOT / os.fsdecode(item)
        for item in result.stdout.split(b"\0")
        if item
    ]
    return sorted(
        path for path in paths
        if not EXCLUDED_PARTS.intersection(path.relative_to(ROOT).parts)
        and path.is_file()
    )


def main() -> int:
    files = tracked_javascript_files()
    failures: list[tuple[Path, str]] = []

    for path in files:
        relative = path.relative_to(ROOT).as_posix()
        try:
            source = path.read_bytes()
            result = subprocess.run(
                ["node", "--input-type=module", "--check"],
                cwd=ROOT,
                input=source,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=15,
                check=False,
            )
            if result.returncode:
                message = result.stderr.decode("utf-8", errors="replace").strip()
                failures.append((path, message or "Node.js syntax check failed"))
        except (OSError, subprocess.TimeoutExpired) as exc:
            failures.append((path, str(exc)))

    for path, message in failures:
        relative = path.relative_to(ROOT).as_posix()
        first_line = message.splitlines()[0].replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")
        print(f"::error file={relative}::{first_line}")
        print(f"FAIL {relative}: {message}")

    if failures:
        print(f"\nFAIL: {len(failures)} of {len(files)} tracked JavaScript file(s) failed syntax validation.")
        return 1

    print(f"PASS: all {len(files)} tracked JavaScript file(s) passed syntax validation.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
