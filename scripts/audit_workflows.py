#!/usr/bin/env python3
"""Inventory GitHub workflow directory without deleting or modifying files."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = ROOT / ".github" / "workflows"
VALID_SUFFIXES = {".yml", ".yaml"}


def main() -> int:
    if not WORKFLOWS.is_dir():
        print("No .github/workflows directory found.")
        return 0

    files = sorted(path for path in WORKFLOWS.rglob("*") if path.is_file())
    workflow_files = [path for path in files if path.suffix.lower() in VALID_SUFFIXES]
    non_workflow_files = [path for path in files if path.suffix.lower() not in VALID_SUFFIXES]
    result = {
        "workflow_directory_files": len(files),
        "yaml_workflow_candidates": len(workflow_files),
        "non_yaml_files_not_loaded_by_github_actions": [
            path.relative_to(ROOT).as_posix() for path in non_workflow_files
        ],
        "yaml_files": [path.relative_to(ROOT).as_posix() for path in workflow_files],
        "note": "Inventory only. No workflow was deleted, renamed, or disabled.",
    }
    output = ROOT / "workflow-audit-report.json"
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
