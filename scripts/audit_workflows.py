#!/usr/bin/env python3
"""Inventory GitHub workflow files and detect YAML that is not an Actions workflow."""

from __future__ import annotations

import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = ROOT / ".github" / "workflows"
VALID_SUFFIXES = {".yml", ".yaml"}


def main() -> int:
    if not WORKFLOWS.is_dir():
        print("No .github/workflows directory found.")
        return 0

    files = sorted(path for path in WORKFLOWS.rglob("*") if path.is_file())
    yaml_files = [path for path in files if path.suffix.lower() in VALID_SUFFIXES]
    non_yaml_files = [path for path in files if path.suffix.lower() not in VALID_SUFFIXES]
    valid_workflows = []
    invalid_yaml = []

    for path in yaml_files:
        relative = path.relative_to(ROOT).as_posix()
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, yaml.YAMLError) as exc:
            invalid_yaml.append({"path": relative, "reason": type(exc).__name__})
            continue

        # PyYAML's YAML 1.1 resolver may parse the GitHub key "on" as True.
        has_trigger = isinstance(data, dict) and ("on" in data or True in data)
        has_jobs = isinstance(data, dict) and isinstance(data.get("jobs"), dict)
        if has_trigger and has_jobs:
            valid_workflows.append(relative)
        else:
            invalid_yaml.append({
                "path": relative,
                "reason": "missing top-level Actions trigger or jobs mapping",
            })

    result = {
        "workflow_directory_files": len(files),
        "yaml_candidates": len(yaml_files),
        "valid_actions_workflows": len(valid_workflows),
        "invalid_or_non_workflow_yaml": invalid_yaml,
        "non_yaml_files_not_loaded_by_github_actions": [
            path.relative_to(ROOT).as_posix() for path in non_yaml_files
        ],
        "valid_workflows": valid_workflows,
        "note": "Inventory only. No files are deleted, renamed, or disabled.",
    }
    output = ROOT / "workflow-audit-report.json"
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
