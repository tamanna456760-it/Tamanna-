#!/usr/bin/env python3
"""Read-only inventory of files stored in .github/workflows.

This tool never moves, edits, deletes, executes, or stages repository files.
It classifies entries by extension and checks whether YAML files look like
GitHub Actions workflows. Full YAML parsing is intentionally not required.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

WORKFLOW_SUFFIXES = {".yml", ".yaml"}
SOURCE_SUFFIXES = {
    ".py", ".js", ".mjs", ".cjs", ".ts", ".tsx", ".jsx", ".sh",
    ".bash", ".zsh", ".java", ".kt", ".dart", ".go", ".rs", ".php",
    ".rb", ".c", ".h", ".cpp", ".cs", ".swift",
}
CONFIG_SUFFIXES = {
    ".json", ".xml", ".toml", ".ini", ".cfg", ".properties", ".env",
    ".md", ".txt",
}


def classify(path: Path, text: str | None) -> tuple[str, str]:
    suffix = path.suffix.lower()
    if suffix in WORKFLOW_SUFFIXES:
        if text is None:
            return "yaml-needs-review", "Could not read file as UTF-8"
        has_jobs = any(line.strip() == "jobs:" for line in text.splitlines())
        has_on = any(
            line.strip() == "on:" or line.startswith("on:")
            for line in text.splitlines()
        )
        if has_jobs and has_on:
            return "candidate-github-workflow", "Contains top-level on/jobs markers; validate YAML and actions"
        return "yaml-config-or-invalid-workflow", "YAML extension but expected on/jobs markers were not both found"
    if suffix in SOURCE_SUFFIXES:
        return "source-file-misplaced", "Source-code extension inside the workflow directory; inspect references before moving"
    if suffix in CONFIG_SUFFIXES or not suffix:
        return "config-or-document-misplaced", "Not a GitHub Actions workflow by extension; inspect purpose and references"
    return "other-needs-review", "Unknown or uncommon file type; do not delete automatically"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(".github/workflows"))
    parser.add_argument("--output", type=Path, help="Optional JSON output path")
    args = parser.parse_args()

    root = args.root
    if not root.exists():
        parser.error(f"directory does not exist: {root}")
    if not root.is_dir():
        parser.error(f"not a directory: {root}")

    entries = []
    for path in sorted(p for p in root.rglob("*") if p.is_file()):
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeError, OSError):
            text = None
        category, reason = classify(path, text)
        entries.append({
            "path": path.as_posix(),
            "extension": path.suffix.lower() or "(none)",
            "category": category,
            "reason": reason,
            "bytes": path.stat().st_size,
        })

    summary = {}
    for item in entries:
        summary[item["category"]] = summary.get(item["category"], 0) + 1

    report = {
        "root": root.as_posix(),
        "read_only": True,
        "files_scanned": len(entries),
        "summary": summary,
        "files": entries,
        "safety_note": "No files were moved, changed, deleted, staged, or executed. Review references before any relocation.",
    }
    rendered = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
