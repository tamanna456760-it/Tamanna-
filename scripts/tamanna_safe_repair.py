#!/usr/bin/env python3
"""Tamanna AI Safe Repair — backup, conservative fixes, and diagnostics."""

from pathlib import Path
from datetime import datetime, timezone
import argparse
import json
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parent.parent
STAMP = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
BACKUP = ROOT / ".tamanna-repair-backup" / STAMP
REPORT = ROOT / "tamanna_repair_report.json"

SAFE_AUTO_HEAL = r"""name: Tamanna Auto Heal - Safe Validation

on:
  workflow_dispatch:
  push:
    branches: [main]
  pull_request:
    branches: [main]

permissions:
  contents: read

concurrency:
  group: tamanna-safe-validation-${{ github.ref }}
  cancel-in-progress: true

jobs:
  validate:
    name: Read-only repository validation
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Check whitespace errors
        run: git diff --check

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Check selected Python files
        shell: bash
        run: |
          set -u
          files=()
          for file in \
            scripts/analyzer.py \
            scripts/fixer.py \
            scripts/tamanna_repo_repair.py \
            scripts/tamanna_safe_repair.py
          do
            if [ -f "$file" ]; then
              files+=("$file")
            fi
          done

          if [ "${#files[@]}" -eq 0 ]; then
            echo "No selected Python files found."
            exit 1
          fi

          python -m py_compile "${files[@]}"
          echo "Selected Python files passed syntax validation."
"""

def git_root_check():
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        cwd=ROOT, text=True, capture_output=True
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"Not inside a Git repository: {ROOT}\n{result.stderr.strip()}"
        )

def save_backup(path):
    relative = path.relative_to(ROOT)
    destination = BACKUP / relative
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(path.read_bytes())

def write_if_changed(path, new_text, apply, changes):
    old_text = path.read_text(encoding="utf-8")
    if old_text == new_text:
        changes.append({"file": str(path.relative_to(ROOT)), "status": "already_safe"})
        return

    changes.append({"file": str(path.relative_to(ROOT)), "status": "would_change"})

    if not apply:
        return

    save_backup(path)
    path.write_text(new_text, encoding="utf-8")
    changes[-1]["status"] = "changed"
    print(f"REPAIRED: {path.relative_to(ROOT)}")

def patch_altimate(path, apply, changes):
    if not path.exists():
        changes.append({
            "file": str(path.relative_to(ROOT)),
            "status": "missing"
        })
        return

    text = path.read_text(encoding="utf-8")

    # Pass the comment through an environment variable rather than
    # interpolating untrusted comment text directly into a shell command.
    pattern = re.compile(
        r"(?m)^(?P<step_indent>[ \t]*)- name: Parse command\n"
        r"(?P<field_indent>[ \t]*)shell: bash\n"
        r"(?P<run_indent>[ \t]*)run: \|\n"
        r"(?P<body_indent>[ \t]*)COMMENT='\$\{\{ github\.event\.comment\.body \}\}'"
    )

    match = pattern.search(text)
    if not match:
        if "COMMENT='${{ github.event.comment.body }}'" in text:
            changes.append({
                "file": str(path.relative_to(ROOT)),
                "status": "unsafe_interpolation_found_but_layout_not_recognized"
            })
        else:
            changes.append({
                "file": str(path.relative_to(ROOT)),
                "status": "pattern_not_found_review_manually"
            })
        return

    step_indent = match.group("step_indent")
    field_indent = match.group("field_indent")
    run_indent = match.group("run_indent")
    body_indent = match.group("body_indent")

    replacement = (
        f"{step_indent}- name: Parse command\n"
        f"{field_indent}env:\n"
        f"{field_indent}  COMMENT: ${{{{ github.event.comment.body }}}}\n"
        f"{field_indent}shell: bash\n"
        f"{run_indent}run: |\n"
        f'{body_indent}CMD=$(printf \'%s\\n\' "$COMMENT" | awk \'{{print $1}}\')'
    )

    updated = text[:match.start()] + replacement + text[match.end():]
    write_if_changed(path, updated, apply, changes)

def diagnose_python_files():
    candidates = [
        ROOT / "runner/python/radar.py",
        ROOT / "runner/python/signal.py",
        ROOT / "runner/python/tamanna_ai.py",
        ROOT / "runner/python/tamanna_deep_power.py",
        ROOT / "scripts/analyzer.py",
        ROOT / "scripts/fixer.py",
    ]
    results = []

    for path in candidates:
        if not path.exists():
            results.append({
                "file": str(path.relative_to(ROOT)),
                "status": "missing"
            })
            continue

        result = subprocess.run(
            [sys.executable, "-m", "py_compile", str(path)],
            cwd=ROOT, text=True, capture_output=True
        )
        results.append({
            "file": str(path.relative_to(ROOT)),
            "status": "pass" if result.returncode == 0 else "syntax_error",
            "details": (result.stderr or result.stdout).strip()
        })

    return results

def main():
    parser = argparse.ArgumentParser(
        description="Back up and safely repair selected Tamanna workflow issues."
    )
    parser.add_argument(
        "--apply", action="store_true",
        help="Apply supported changes. Without this option, only preview."
    )
    args = parser.parse_args()

    try:
        git_root_check()
    except RuntimeError as exc:
        print(f"STOP: {exc}")
        return 2

    changes = []
    auto_heal = ROOT / ".github/workflows/auto-heal.yml"
    altimate = ROOT / ".github/workflows/tamanna-ai-altimate.yml"

    print(f"Repository: {ROOT}")
    print(f"Mode: {'APPLY' if args.apply else 'DRY RUN (no files changed)'}")

    if auto_heal.exists():
        write_if_changed(
            auto_heal,
            SAFE_AUTO_HEAL,
            args.apply,
            changes
        )
    else:
        changes.append({
            "file": str(auto_heal.relative_to(ROOT)),
            "status": "missing"
        })

    patch_altimate(altimate, args.apply, changes)

    # Run diagnostics after repairs, but do not modify source Python files.
    python_checks = diagnose_python_files()

    report = {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "repository": str(ROOT),
        "mode": "apply" if args.apply else "dry-run",
        "backup_directory": str(BACKUP) if args.apply else None,
        "workflow_changes": changes,
        "python_diagnostics": python_checks,
        "note": (
            "Python source files are diagnosed only, not automatically rewritten. "
            "GitHub push is not performed."
        )
    }

    REPORT.write_text(
        json.dumps(report, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    print("\n===== WORKFLOW RESULTS =====")
    for item in changes:
        print(f"{item['status']}: {item['file']}")

    print("\n===== PYTHON DIAGNOSTICS =====")
    for item in python_checks:
        print(f"{item['status']}: {item['file']}")
        if item.get("details"):
            print(f"  {item['details']}")

    print(f"\nReport: {REPORT.relative_to(ROOT)}")
    if args.apply:
        print(f"Backup: {BACKUP.relative_to(ROOT)}")
    else:
        print("\nNo source files were changed. Review the preview, then run with --apply.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
PY

python3 -m py_compile scripts/tamanna_safe_repair.py
python3 scripts/tamanna_safe_repair.py
