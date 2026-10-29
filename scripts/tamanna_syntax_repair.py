
#!/usr/bin/env python3
"""Tamanna AI safe Python syntax audit.

Read-only by default. It does not rewrite or delete source files.
Run from any directory inside the repository.
"""

from __future__ import annotations

import ast
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

SKIP_DIRS = {
    ".git", ".venv", "venv", "node_modules",
    "__pycache__", "build", "dist", ".pytest_cache",
}

ROOT = Path(__file__).resolve().parent.parent
REPORT = ROOT / "tamanna_syntax_audit.json"


def scan_python_files():
    results = []

    for path in sorted(ROOT.rglob("*.py")):
        if any(part in SKIP_DIRS for part in path.parts):
            continue

        if path.is_symlink() or not path.is_file():
            continue

        try:
            source = path.read_text(encoding="utf-8")
            ast.parse(source, filename=str(path))
            results.append({
                "file": path.relative_to(ROOT).as_posix(),
                "status": "PASS",
                "line": None,
                "error": None,
            })
        except UnicodeDecodeError as exc:
            results.append({
                "file": path.relative_to(ROOT).as_posix(),
                "status": "ENCODING_ERROR",
                "line": None,
                "error": str(exc),
            })
        except SyntaxError as exc:
            results.append({
                "file": path.relative_to(ROOT).as_posix(),
                "status": "SYNTAX_ERROR",
                "line": exc.lineno,
                "column": exc.offset,
                "error": exc.msg,
                "source_line": exc.text.strip() if exc.text else None,
            })
        except OSError as exc:
            results.append({
                "file": path.relative_to(ROOT).as_posix(),
                "status": "READ_ERROR",
                "line": None,
                "error": str(exc),
            })

    return results


def main():
    if not ROOT.is_dir():
        print(f"ERROR: Repository root not found: {ROOT}")
        return 2

    results = scan_python_files()

    report = {
        "project": "Tamanna AI",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "repository_root": str(ROOT),
        "read_only": True,
        "total_python_files": len(results),
        "passed": sum(r["status"] == "PASS" for r in results),
        "syntax_errors": sum(
            r["status"] == "SYNTAX_ERROR" for r in results
        ),
        "other_errors": sum(
            r["status"] not in {"PASS", "SYNTAX_ERROR"}
            for r in results
        ),
        "results": results,
    }

    REPORT.write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    for item in results:
        if item["status"] != "PASS":
            print(
                f"{item['status']}: {item['file']}:"
                f"{item.get('line') or '-'}: {item['error']}"
            )

    print()
    print(f"Python files scanned: {len(results)}")
    print(f"PASS: {report['passed']}")
    print(f"Syntax errors: {report['syntax_errors']}")
    print(f"Other errors: {report['other_errors']}")
    print(f"Report saved: {REPORT}")

    return 1 if report["syntax_errors"] or report["other_errors"] else 0


if __name__ == "__main__":
    sys.exit(main())
