#!/usr/bin/env python3
"""Tamanna AI: read-only Python syntax audit.

Owner: HM INSAN ALI

This script checks Python syntax without modifying source files.
"""

from pathlib import Path
import sys
import tokenize

ROOT = Path(__file__).resolve().parent.parent
REPORT = ROOT / ".tamanna-review" / "python-audit.txt"

EXCLUDED = {
    ".git",
    ".venv",
    "venv",
    "node_modules",
    "__pycache__",
    ".tamanna-repair-backup",
}

def should_skip(path: Path) -> bool:
    return any(part in EXCLUDED for part in path.parts)

def main() -> int:
    checked = 0
    failures = []

    for path in sorted(ROOT.rglob("*.py")):
        relative = path.relative_to(ROOT)

        if should_skip(relative):
            continue

        checked += 1

        try:
            with tokenize.open(path) as source_file:
                source = source_file.read()

            compile(source, str(relative), "exec")

        except (SyntaxError, IndentationError, TabError) as exc:
            failures.append(
                f"FAIL: {relative}\n"
                f"  Error: {exc.msg}\n"
                f"  Line: {exc.lineno}\n"
                f"  Column: {exc.offset}\n"
            )
        except (OSError, UnicodeError, ValueError) as exc:
            failures.append(
                f"ERROR: {relative}\n"
                f"  {type(exc).__name__}: {exc}\n"
            )

    REPORT.parent.mkdir(parents=True, exist_ok=True)

    lines = [
        "TAMANNA AI - PYTHON SYNTAX AUDIT",
        "Owner: HM INSAN ALI",
        "=" * 42,
        f"Python files checked: {checked}",
        f"Files with errors: {len(failures)}",
        "",
    ]

    lines.extend(failures if failures else ["PASS: No syntax errors found."])
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("\n".join(lines))
    print(f"\nReport saved to: {REPORT.relative_to(ROOT)}")

    return 1 if failures else 0

if __name__ == "__main__":
    sys.exit(main())
PY

python3 -m py_compile scripts/tamanna_python_audit.py
python3 scripts/tamanna_python_audit.py
