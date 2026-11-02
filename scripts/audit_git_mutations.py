#!/usr/bin/env python3
"""Read-only audit for scripts that can mutate or push Git repositories."""
from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path

CODE_SUFFIXES = {".py", ".sh", ".bash", ".js", ".mjs", ".cjs", ".ts", ".bat", ".ps1", ".yml", ".yaml"}
SKIP_PARTS = {".git", ".venv", "venv", "node_modules", "__pycache__", ".pytest_cache"}
RULES = [
    ("force_push", "critical", re.compile(r"\bgit\s+push\b[^\n]*(?:--force\b|\s-f\b)", re.I)),
    ("credential_in_remote_url", "critical", re.compile(r"https?://[^\s/@:]+:[^\s/@]+@github\.com", re.I)),
    ("git_push", "high", re.compile(r"\bgit\s+push\b", re.I)),
    ("stage_all_files", "high", re.compile(r"\bgit\s+add\s+(?:-A\b|--all\b|\.)", re.I)),
    ("git_commit", "medium", re.compile(r"\bgit\s+commit\b", re.I)),
]


def files(root: Path) -> list[Path]:
    try:
        out = subprocess.run(
            ["git", "ls-files", "-z"], cwd=root, check=True,
            capture_output=True, timeout=10,
        ).stdout.decode("utf-8", "replace")
        names = out.split(chr(0))
        return [root / name for name in names if name]
    except (OSError, subprocess.SubprocessError):
        return [p for p in root.rglob("*") if p.is_file()]


def audit(root: Path) -> list[dict]:
    findings = []
    for path in files(root):
        try:
            rel = path.relative_to(root)
            if any(part in SKIP_PARTS for part in rel.parts):
                continue
            if path.suffix.lower() not in CODE_SUFFIXES or path.stat().st_size > 1_000_000:
                continue
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError, ValueError):
            continue
        for rule, severity, pattern in RULES:
            for match in pattern.finditer(text):
                findings.append({
                    "path": rel.as_posix(),
                    "line": text.count("\n", 0, match.start()) + 1,
                    "rule": rule,
                    "severity": severity,
                })
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()
    root = args.root.resolve()
    findings = audit(root)
    report = {
        "mode": "read-only",
        "files_reviewed": len(files(root)),
        "findings_count": len(findings),
        "findings": findings,
        "note": "Matches require human review; this tool never executes or changes repository files.",
    }
    rendered = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
