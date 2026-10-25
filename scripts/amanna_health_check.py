
#!/usr/bin/env python3
"""
Tamanna AI - Main Server Health Check
Owner: HM INSAN ALI

Read-only checks. Does not modify existing server files.
"""

import ast
import importlib.util
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    ROOT / "main.py",
    ROOT / "Main.py",
    ROOT / "requirements.txt",
]

results = []


def check(name, passed, details):
    results.append({
        "check": name,
        "status": "PASS" if passed else "FAIL",
        "details": details,
    })
    print(f"[{'PASS' if passed else 'FAIL'}] {name}: {details}")


def main():
    print("=== TAMANNA AI SERVER HEALTH CHECK ===")
    print("Time:", datetime.now(timezone.utc).isoformat())

    for path in REQUIRED_FILES:
        check(
            f"File: {path.relative_to(ROOT)}",
            path.is_file() and path.stat().st_size > 0,
            "Present and non-empty" if path.is_file()
            and path.stat().st_size > 0 else "Missing or empty",
        )

    for filename in ("main.py", "Main.py"):
        path = ROOT / filename
        if not path.is_file():
            continue

        try:
            ast.parse(path.read_text(encoding="utf-8"), filename=filename)
            check(f"Syntax: {filename}", True, "Valid Python syntax")
        except (SyntaxError, UnicodeDecodeError, OSError) as exc:
            check(f"Syntax: {filename}", False, str(exc))

    main_file = ROOT / "main.py"
    if main_file.is_file():
        try:
            source = main_file.read_text(encoding="utf-8")
            references_main = (
                "Main" in source
                or "main:app" in source
                or "FastAPI" in source
            )
            check(
                "Main entry point",
                references_main,
                "Potential app entry-point reference found"
                if references_main else
                "Could not identify expected app reference; inspect main.py",
            )
        except OSError as exc:
            check("Main entry point", False, str(exc))

    try:
        spec = importlib.util.find_spec("fastapi")
        check(
            "FastAPI dependency",
            spec is not None,
            "Installed" if spec else
            "Not installed in this Python environment",
        )
    except (ImportError, ValueError) as exc:
        check("FastAPI dependency", False, str(exc))

    report = {
        "system": "Tamanna AI",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "checks": results,
        "passed": sum(r["status"] == "PASS" for r in results),
        "failed": sum(r["status"] == "FAIL" for r in results),
    }

    report_dir = ROOT / "reports"
    report_dir.mkdir(exist_ok=True)
    report_path = report_dir / "tamanna_health_check.json"
    report_path.write_text(
        json.dumps(report, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print("\nReport:", report_path.relative_to(ROOT))
    print(f"Passed: {report['passed']} | Failed: {report['failed']}")

    return 1 if report["failed"] else 0


if __name__ == "__main__":
    sys.exit(main())
