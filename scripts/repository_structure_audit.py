#!/usr/bin/env python3
"""Read-only repository structure audit. Never moves or deletes files."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from typing import Any

IGNORED_DIRS = {".git", ".venv", "venv", "__pycache__", "node_modules", ".pytest_cache"}


def audit_repository(root: Path) -> dict[str, Any]:
    root = root.resolve()
    files = [p for p in root.rglob("*") if p.is_file()
             and not any(part in IGNORED_DIRS for part in p.relative_to(root).parts)]
    workflow_dir = root / ".github" / "workflows"
    misplaced = sorted(p.relative_to(root).as_posix() for p in workflow_dir.rglob("*")
                       if p.is_file() and p.suffix.lower() not in {".yml", ".yaml"}) if workflow_dir.is_dir() else []
    empty_python = sorted(p.relative_to(root).as_posix() for p in files
                          if p.suffix == ".py" and p.stat().st_size == 0)
    empty_files = sorted(p.relative_to(root).as_posix() for p in files if p.stat().st_size == 0)
    suspicious = sorted(p.relative_to(root).as_posix() for p in files
                        if p.suffix.lower() in {".ymal", ".ymls", ".jaon", ".jason"})
    pyc = sorted(
        p.relative_to(root).as_posix()
        for p in root.rglob("*.pyc")
        if p.is_file()
        and not any(part in IGNORED_DIRS for part in p.relative_to(root).parts)
    )
    dirs_without_init = set()
    for p in files:
        if p.suffix == ".py" and p.parent != root:
            if not (p.parent / "__init__.py").exists():
                dirs_without_init.add(p.parent.relative_to(root).as_posix())
    summary = {
        "files": len(files), "workflow_non_workflow_count": len(misplaced),
        "empty_python_count": len(empty_python), "empty_file_count": len(empty_files),
        "suspicious_extension_count": len(suspicious), "pyc_count": len(pyc),
        "python_dirs_without_init_count": len(dirs_without_init),
    }
    return {
        "root": str(root), "file_count": len(files), "summary": summary,
        "workflow_non_workflow_files": misplaced, "empty_python_files": empty_python,
        "empty_files": empty_files, "suspicious_extensions": suspicious,
        "compiled_python_files": pyc, "python_dirs_without_init": sorted(dirs_without_init),
    }


def render_markdown(report: dict[str, Any]) -> str:
    s = report["summary"]
    lines = [
        "# Tamanna Repository Structure Audit", "",
        "> Read-only report: this scanner never moves, deletes, or rewrites source files.", "",
        f"- Files scanned: **{s['files']}**",
        f"- Non-workflow files in .github/workflows/: **{s['workflow_non_workflow_count']}**",
        f"- Empty Python files: **{s['empty_python_count']}**",
        f"- Empty files, all types: **{s['empty_file_count']}**",
        f"- Suspicious extensions: **{s['suspicious_extension_count']}**",
        f"- .pyc files present: **{s['pyc_count']}**",
        f"- Python directories without __init__.py: **{s['python_dirs_without_init_count']}**", ""
    ]
    for key, title in [
        ("workflow_non_workflow_files", "Misplaced workflow-directory files"),
        ("empty_python_files", "Empty Python files"),
        ("suspicious_extensions", "Suspicious extensions"),
        ("compiled_python_files", "Compiled Python files"),
    ]:
        lines.extend([f"## {title}", ""])
        values = report[key]
        lines.extend([f"- {p}" for p in values] if values else ["- None detected"])
        lines.append("")
    lines.extend([
        "## Safe remediation policy", "",
        "1. Check imports, references, CI usage and runtime ownership before moving files.",
        "2. Implement empty modules only after defining their public API and tests.",
        "3. Keep executable GitHub Actions workflow definitions in .yml/.yaml files.",
        "4. Do not delete backups, binaries, data or unknown files based on extension alone.", ""
    ])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--format", choices=("json", "markdown"), default="markdown")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = audit_repository(args.root)
    output = json.dumps(report, indent=2) if args.format == "json" else render_markdown(report)
    if args.output:
        args.output.write_text(output + "\n", encoding="utf-8")
    else:
        print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
