#!/usr/bin/env python3
"""Tamanna AI workflow hardening.
Backs up existing workflows before applying safe, read-only replacements.
"""

from pathlib import Path
from datetime import datetime, timezone
import argparse
import shutil
import sys

ROOT = Path(__file__).resolve().parent.parent
STAMP = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
BACKUP = ROOT / ".tamanna-repair-backup" / STAMP

SAFE_AUDIT = r'''name: Tamanna Safe Repository Audit

on:
  workflow_dispatch:
  push:
    branches: [main]
  pull_request:
    branches: [main]

permissions:
  contents: read

concurrency:
  group: tamanna-safe-audit-${{ github.ref }}
  cancel-in-progress: true

jobs:
  audit:
    runs-on: ubuntu-latest
    timeout-minutes: 15
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Check available repair tools
        shell: bash
        run: |
          set -eu
          test -f scripts/analyzer.py
          test -f scripts/fixer.py
          python -m py_compile scripts/analyzer.py scripts/fixer.py

      - name: Run read-only analyzer
        env:
          TAMANNA_ANALYZER_REPORT: ${{ runner.temp }}/tamanna_analyzer_report.json
        run: python scripts/analyzer.py

      - name: Generate review-only fix plan
        env:
          TAMANNA_ANALYZER_REPORT: ${{ runner.temp }}/tamanna_analyzer_report.json
          TAMANNA_FIXER_REPORT: ${{ runner.temp }}/tamanna_fix_plan.json
        run: python scripts/fixer.py

      - name: Upload reports
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: tamanna-safe-audit-${{ github.run_id }}
          path: |
            ${{ runner.temp }}/tamanna_analyzer_report.json
            ${{ runner.temp }}/tamanna_fix_plan.json
          if-no-files-found: warn
          retention-days: 14
'''

SAFE_COMMENT_AUDIT = r'''name: Tamanna Comment Command Audit

on:
  issue_comment:
    types: [created]
  workflow_dispatch:

permissions:
  contents: read
  issues: read
  pull-requests: read

jobs:
  inspect:
    if: github.event_name == 'workflow_dispatch' || github.event.comment.body != ''
    runs-on: ubuntu-latest
    timeout-minutes: 5
    steps:
      - name: Safely inspect comment
        if: github.event_name == 'issue_comment'
        env:
          COMMENT_BODY: ${{ github.event.comment.body }}
          COMMENT_AUTHOR: ${{ github.event.comment.user.login }}
          COMMENT_ASSOCIATION: ${{ github.event.comment.author_association }}
        shell: bash
        run: |
          set -eu
          python - <<'PYCODE'
          import os
          body = os.environ.get("COMMENT_BODY", "")
          author = os.environ.get("COMMENT_AUTHOR", "")
          association = os.environ.get("COMMENT_ASSOCIATION", "")
          first = body.strip().split(maxsplit=1)[0] if body.strip() else ""
          allowed = {"/deploy", "/heal", "/chaos"}
          if first in allowed:
              print("Recognized command:", first)
              print("Author:", author)
              print("Association:", association)
              print("Execution disabled: manual review and authorization are required.")
          else:
              print("No recognized Tamanna command.")
          PYCODE
'''

SAFE_SECURITY = r'''name: Tamanna Security and Syntax Checks

on:
  workflow_dispatch:
  push:
    branches: [main]
  pull_request:
    branches: [main]

permissions:
  contents: read

jobs:
  checks:
    runs-on: ubuntu-latest
    timeout-minutes: 20
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Check Python syntax
        shell: bash
        run: |
          set -u
          python - <<'PYCODE'
          from pathlib import Path
          import py_compile
          import sys

          excluded = {".git", ".venv", "venv", "node_modules", "__pycache__"}
          failures = []
          count = 0

          for path in Path(".").rglob("*.py"):
              if any(part in excluded for part in path.parts):
                  continue
              count += 1
              try:
                  py_compile.compile(str(path), doraise=True)
              except Exception as exc:
                  failures.append((str(path), str(exc)))

          print(f"Checked {count} Python files.")
          for path, error in failures:
              print(f"SYNTAX ERROR: {path}: {error}")

          if failures:
              sys.exit(1)
          PYCODE

      - name: Check whitespace errors
        run: git diff --check
'''

# These workflows are deliberately changed to read-only audit modes.
# The old auto-healing, auto-upgrade and auto-sync write actions are disabled.
REPLACEMENTS = {
    ".github/workflows/auto-heal.yml": SAFE_AUDIT,
    ".github/workflows/auto-upgrade.yml": SAFE_AUDIT,
    ".github/workflows/auto-sync-bd-king-r7.yml": SAFE_AUDIT,
    ".github/workflows/tamanna-ai-altimate.yml": SAFE_COMMENT_AUDIT,
    ".github/workflows/security-checks.yml": SAFE_SECURITY,
}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Back up and apply changes. Without this flag, only preview.",
    )
    args = parser.parse_args()

    print("Tamanna workflow hardening")
    print("Repository:", ROOT)
    print("Mode:", "APPLY" if args.apply else "DRY RUN (no changes)")
    print()

    missing = []
    for relative, content in REPLACEMENTS.items():
        target = ROOT / relative
        if not target.is_file():
            missing.append(relative)
            print("SKIP (file not found):", relative)
            continue

        print(("UPDATE: " if args.apply else "WOULD UPDATE: "), relative)
        if args.apply:
            backup = BACKUP / relative
            backup.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(target, backup)
            target.write_text(content.rstrip() + "\n", encoding="utf-8")

    if args.apply:
        print()
        print("Backup directory:", BACKUP)
        print("Workflow files updated:", len(REPLACEMENTS) - len(missing))
        print("Note: /deploy, /heal and /chaos are logged only, never executed.")
    else:
        print()
        print("No files changed. Review the list, then rerun with --apply.")

    if missing:
        print("Some workflow files were not found; they were left unchanged.")

if __name__ == "__main__":
    main()
PY
