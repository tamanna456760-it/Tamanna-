#!/usr/bin/env python3

import json
import shutil
import subprocess
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).parent

IGNORE_DIRS = {
    ".git",
    "__pycache__",
    ".venv",
    "venv",
    "node_modules",
}

report = {
    "generated_at": datetime.now().isoformat(),
    "files_checked": 0,
    "issues": []
}

ruff = shutil.which("ruff")

for file in ROOT.rglob("*.py"):

    if any(part in IGNORE_DIRS for part in file.parts):
        continue

    report["files_checked"] += 1

    if ruff:
        result = subprocess.run(
            [ruff, "check", str(file)],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            report["issues"].append({
                "file": str(file.relative_to(ROOT)),
                "tool": "ruff",
                "output": result.stdout.strip()
            })

    else:
        result = subprocess.run(
            ["python3", "-m", "py_compile", str(file)],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            report["issues"].append({
                "file": str(file.relative_to(ROOT)),
                "tool": "py_compile",
                "output": result.stderr.strip()
            })

with open("lint_report.json", "w", encoding="utf-8") as f:
    json.dump(report, f, indent=4)

print("=" * 50)
print("Tamanna Lint & Issue Detector")
print("=" * 50)
print(f"Files checked : {report['files_checked']}")
print(f"Issues found  : {len(report['issues'])}")
print("Report saved  : lint_report.json")
