#!/usr/bin/env python3

import json
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).parent

IGNORE = {
    ".git",
    "__pycache__",
    ".venv",
    "venv",
    "node_modules",
}

report = {
    "generated_at": datetime.now().isoformat(),
    "files_scanned": 0,
    "issues": [],
}

for file in ROOT.rglob("*.py"):
    if any(part in IGNORE for part in file.parts):
        continue

    report["files_scanned"] += 1

    try:
        with open(file, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except Exception as e:
        report["issues"].append({
            "file": str(file.relative_to(ROOT)),
            "issue": f"Could not read file: {e}"
        })
        continue

    for number, line in enumerate(lines, start=1):
        if line.rstrip("\n") != line.rstrip():
            report["issues"].append({
                "file": str(file.relative_to(ROOT)),
                "line": number,
                "issue": "Trailing whitespace"
            })

        if "\t" in line:
            report["issues"].append({
                "file": str(file.relative_to(ROOT)),
                "line": number,
                "issue": "Tab character found"
            })

        if len(line.rstrip("\n")) > 100:
            report["issues"].append({
                "file": str(file.relative_to(ROOT)),
                "line": number,
                "issue": "Line longer than 100 characters"
            })

        if "TODO" in line:
            report["issues"].append({
                "file": str(file.relative_to(ROOT)),
                "line": number,
                "issue": "TODO comment"
            })

with open("issues_report.json", "w", encoding="utf-8") as f:
    json.dump(report, f, indent=4)

print("=" * 50)
print("Tamanna Auto Issue Scanner")
print("=" * 50)
print(f"Files scanned : {report['files_scanned']}")
print(f"Issues found  : {len(report['issues'])}")
print("Report saved  : issues_report.json")
