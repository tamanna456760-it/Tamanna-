#!/usr/bin/env python3

import json
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).parent

IGNORE_DIRS = {
    ".git",
    "__pycache__",
    ".venv",
    "venv",
    "node_modules",
    ".idea",
    ".vscode",
}

report = {
    "generated_at": datetime.now().isoformat(),
    "project_root": str(ROOT),
    "summary": {},
    "python_files": [],
    "javascript_files": [],
    "shell_files": [],
    "markdown_files": [],
}

for path in ROOT.rglob("*"):
    if not path.is_file():
        continue

    if any(part in IGNORE_DIRS for part in path.parts):
        continue

    item = {
        "name": path.name,
        "path": str(path.relative_to(ROOT)),
        "size_bytes": path.stat().st_size,
    }

    if path.suffix == ".py":
        report["python_files"].append(item)
    elif path.suffix == ".js":
        report["javascript_files"].append(item)
    elif path.suffix == ".sh":
        report["shell_files"].append(item)
    elif path.suffix == ".md":
        report["markdown_files"].append(item)

report["summary"] = {
    "python": len(report["python_files"]),
    "javascript": len(report["javascript_files"]),
    "shell": len(report["shell_files"]),
    "markdown": len(report["markdown_files"]),
    "total_files": (
        len(report["python_files"])
        + len(report["javascript_files"])
        + len(report["shell_files"])
        + len(report["markdown_files"])
    ),
}

with open("code_report.json", "w", encoding="utf-8") as f:
    json.dump(report, f, indent=4)

print("=" * 50)
print("📁 Tamanna Auto Code Manager")
print("=" * 50)
print(f"Python Files     : {report['summary']['python']}")
print(f"JavaScript Files : {report['summary']['javascript']}")
print(f"Shell Files      : {report['summary']['shell']}")
print(f"Markdown Files   : {report['summary']['markdown']}")
print(f"Total Files      : {report['summary']['total_files']}")
print("\n✅ Report saved as code_report.json")
