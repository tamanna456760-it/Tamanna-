
#!/usr/bin/env python3
"""
Tamanna AI - Full System Read-Only Audit
Owner: HM INSAN ALI

Checks:
- Required files and directories
- Empty Python files
- Python syntax errors
- requirements.txt presence
- GitHub Actions workflow YAML parsing (if PyYAML is installed)
- Potentially tracked secret/config files

This script NEVER modifies or deletes project files.
"""

from __future__ import annotations

import ast
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / "reports"

REQUIRED = [
    "main.py",
    "Main.py",
    "requirements.txt",
    ".env.example",
    "tamanna_ai",
    "tamanna_ai/core",
    "tamanna_ai/ai_core",
    "tamanna_ai/agents",
    "tamanna_ai/api",
    "modules/tamanna",
    "tests",
    ".github/workflows",
]

SKIP_DIRS = {
    ".git", ".venv", "venv", "node_modules",
    "__pycache__", ".mypy_cache", ".pytest_cache",
    "dist", "build",
}

findings = []


def add(severity, path, message):
    findings.append({
        "severity": severity,
        "path": str(path),
        "message": message,
    })


def run_git(*args):
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=ROOT,
            text=True,
            capture_output=True,
            timeout=15,
            check=False,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except (OSError, subprocess.TimeoutExpired):
        pass
    return None


def check_required_paths():
    print("\n[1] Required files and directories")

    for item in REQUIRED:
        path = ROOT / item

        if not path.exists():
            add("HIGH", item, "Required path is missing")
            print(f"MISSING  {item}")
        elif path.is_file() and path.stat().st_size == 0:
            add("MEDIUM", item, "File exists but is empty")
            print(f"EMPTY    {item}")
        else:
            print(f"OK       {item}")


def python_files():
    for current, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for name in files:
            if name.endswith(".py"):
                yield Path(current) / name


def check_python_syntax():
    print("\n[2] Python syntax")

    total = 0
    errors = 0

    for path in python_files():
        total += 1
        relative = path.relative_to(ROOT)

        try:
            source = path.read_text(encoding="utf-8")
            if not source.strip():
                add("MEDIUM", relative, "Empty Python file")
                print(f"EMPTY    {relative}")
                continue

            ast.parse(source, filename=str(relative))

        except UnicodeDecodeError:
            add("MEDIUM", relative, "File is not valid UTF-8")
            errors += 1
            print(f"ENCODING {relative}")

        except SyntaxError as exc:
            add(
                "HIGH",
                relative,
                f"Syntax error at line {exc.lineno}: {exc.msg}",
            )
            errors += 1
            print(f"SYNTAX   {relative}:{exc.lineno}: {exc.msg}")

    print(f"Checked {total} Python files; syntax errors: {errors}")


def check_dependencies():
    print("\n[3] Dependency manifest")

    req = ROOT / "requirements.txt"

    if not req.is_file():
        add("HIGH", "requirements.txt", "Dependency manifest missing")
        return

    try:
        lines = req.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        add("HIGH", "requirements.txt", f"Cannot read: {exc}")
        return

    packages = [
        line.strip()
        for line in lines
        if line.strip()
        and not line.lstrip().startswith("#")
        and not line.lstrip().startswith("-")
    ]

    if not packages:
        add("HIGH", "requirements.txt", "No dependency entries found")

    print(f"Dependency entries: {len(packages)}")

    if (ROOT / "pyproject.toml").exists():
        print("Found pyproject.toml")
    if (ROOT / "uv.lock").exists():
        print("Found uv.lock")
    if (ROOT / "poetry.lock").exists():
        print("Found poetry.lock")


def check_workflows():
    print("\n[4] GitHub Actions workflow files")

    workflow_dir = ROOT / ".github" / "workflows"

    if not workflow_dir.is_dir():
        add("HIGH", ".github/workflows", "Workflow directory missing")
        return

    files = sorted(
        list(workflow_dir.glob("*.yml"))
        + list(workflow_dir.glob("*.yaml"))
    )

    if not files:
        add("MEDIUM", ".github/workflows", "No YAML workflows found")

    try:
        import yaml
    except ImportError:
        print("PyYAML unavailable; YAML syntax check skipped.")
        print("Install locally with: python3 -m pip install PyYAML")
        return

    for path in files:
        relative = path.relative_to(ROOT)

        try:
            content = path.read_text(encoding="utf-8")
            # GitHub Actions uses the key 'on'; BaseLoader avoids
            # YAML 1.1 interpreting it as a boolean.
            yaml.load(content, Loader=yaml.BaseLoader)
            print(f"YAML OK  {relative}")
        except Exception as exc:
            add("HIGH", relative, f"YAML parse error: {exc}")
            print(f"YAML ERR {relative}: {exc}")


def check_tracked_sensitive_names():
    print("\n[5] Git-tracked sensitive filenames")

    tracked = run_git("ls-files")
    if tracked is None:
        print("Git tracking check unavailable.")
        return

    sensitive_names = {
        ".env",
        "token.txt",
        "credentials.json",
        "id_rsa",
        "id_ed25519",
    }

    matches = []

    for name in tracked.splitlines():
        path = Path(name)
        if path.name in sensitive_names:
            matches.append(name)

    if matches:
        for name in matches:
            add(
                "HIGH",
                name,
                "Sensitive-looking filename is Git-tracked; inspect locally",
            )
            print(f"REVIEW   {name}")
        print("Do not print or upload secret contents to audit logs.")
    else:
        print("No exact sensitive filenames detected.")


def main():
    print("=" * 60)
    print("TAMANNA AI - FULL SYSTEM AUDIT")
    print("Owner: HM INSAN ALI")
    print(f"Root: {ROOT}")
    print("=" * 60)

    check_required_paths()
    check_python_syntax()
    check_dependencies()
    check_workflows()
    check_tracked_sensitive_names()

    report = {
        "system": "Tamanna AI",
        "audit_type": "read-only",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "root": str(ROOT),
        "finding_count": len(findings),
        "findings": findings,
    }

    REPORT_DIR.mkdir(exist_ok=True)
    report_path = REPORT_DIR / "tamanna_full_audit.json"
    report_path.write_text(
        json.dumps(report, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print("\n" + "=" * 60)
    print(f"Findings: {len(findings)}")
    print(f"Report: {report_path.relative_to(ROOT)}")
    print("=" * 60)

    high = sum(1 for item in findings if item["severity"] == "HIGH")
    return 1 if high else 0


if __name__ == "__main__":
    raise SystemExit(main())
