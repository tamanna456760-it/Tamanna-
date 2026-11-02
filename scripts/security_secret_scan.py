#!/usr/bin/env python3
"""Read-only scanner for common accidentally committed credentials.

Values are never printed. Only file, line, and rule identifiers are reported.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

RULES = {
    "github_pat": re.compile(r"github_pat_[A-Za-z0-9_]{20,}"),
    "github_token": re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{20,}\b"),
    "google_api_key": re.compile(r"\bAIza[0-9A-Za-z_-]{30,}\b"),
    "aws_access_key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "private_key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "openai_style_key": re.compile(r"\bsk-[A-Za-z0-9_-]{32,}\b"),
}
SKIP_PARTS = {".git", ".venv", "venv", "node_modules", "__pycache__", ".pytest_cache"}
SKIP_NAMES = {".env", ".env.local", ".env.production"}


def tracked_files(root: Path) -> list[Path]:
    try:
        result = subprocess.run(
            ["git", "ls-files", "-z"],
            cwd=root,
            check=True,
            capture_output=True,
            timeout=10,
        )
        names = result.stdout.decode("utf-8", "replace").split("\0")
        return [root / name for name in names if name]
    except (OSError, subprocess.SubprocessError):
        return [
            path for path in root.rglob("*")
            if path.is_file() and not any(part in SKIP_PARTS for part in path.parts)
        ]


def scan(root: Path) -> list[dict]:
    findings = []
    for path in tracked_files(root):
        try:
            rel = path.relative_to(root)
            if any(part in SKIP_PARTS for part in rel.parts) or path.name in SKIP_NAMES:
                continue
            if path.suffix.lower() in {".png", ".jpg", ".jpeg", ".gif", ".webp", ".pdf", ".zip", ".sqlite", ".db"}:
                continue
            if path.stat().st_size > 2_000_000:
                continue
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError, ValueError):
            continue
        for rule, pattern in RULES.items():
            for match in pattern.finditer(text):
                findings.append({
                    "path": rel.as_posix(),
                    "line": text.count("\n", 0, match.start()) + 1,
                    "rule": rule,
                })
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."))
    args = parser.parse_args()
    root = args.root.resolve()
    findings = scan(root)
    if findings:
        for item in findings:
            print(f"FAIL {item['rule']} {item['path']}:{item['line']}")
        print(f"Credential-like findings: {len(findings)}")
        return 1
    print("PASS: no matching credential patterns found in scanned tracked files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
