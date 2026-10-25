
#!/usr/bin/env python3
"""Tamanna AI real FastAPI health smoke test."""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def main():
    checks = []

    def record(name, passed, detail):
        checks.append({
            "name": name,
            "status": "PASS" if passed else "FAIL",
            "detail": detail,
        })
        print(f"[{'PASS' if passed else 'FAIL'}] {name}: {detail}")

    try:
        from Main import app
        record("Import FastAPI app", True, "Main.app loaded")
    except Exception as exc:
        record("Import FastAPI app", False, f"{type(exc).__name__}: {exc}")
        return save_report(checks)

    try:
        from fastapi.testclient import TestClient

        with TestClient(app) as client:
            response = client.get("/health")

        passed = response.status_code == 200
        record(
            "GET /health",
            passed,
            f"HTTP {response.status_code}; body={response.text[:500]}",
        )
    except Exception as exc:
        record("GET /health", False, f"{type(exc).__name__}: {exc}")

    return save_report(checks)


def save_report(checks):
    report = {
        "system": "Tamanna AI",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "checks": checks,
        "failed": sum(c["status"] == "FAIL" for c in checks),
    }

    path = ROOT / "reports" / "tamanna_health_check.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(report, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print(f"Report saved: {path.relative_to(ROOT)}")
    return 1 if report["failed"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
