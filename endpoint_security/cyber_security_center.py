#!/usr/bin/env python3
"""Tamanna AI Cyber Security Center: safe, read-only audit orchestration.

The default run inspects the local checkout only. An optional TLS check connects
only to the explicitly supplied hostname on the explicitly selected port.
No port discovery, exploitation, mutation, or automatic remediation is done.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

from endpoint_security.dependency_checker import check_requirements
from endpoint_security.tls_certificate_checker import check_tls_certificate
from tamanna_ai.security.ethical_audit import run_ethical_audit

HOST_RE = re.compile(
    r"^(?=.{1,253}$)(?:[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?)(?:\.(?:[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?))*$"
)


def run_center(root: str | Path, tls_host: str | None = None, tls_port: int = 443) -> dict[str, Any]:
    """Run local repository checks and, only when requested, one TLS check."""
    base = Path(root).resolve()
    checks: list[dict[str, Any]] = []

    try:
        audit = run_ethical_audit(base)
        checks.append({"name": "repository_posture", "status": audit["summary"]["status"], "report": audit})
    except Exception as exc:
        checks.append({
            "name": "repository_posture",
            "status": "ERROR",
            "detail": f"Audit failed ({type(exc).__name__}).",
        })

    requirements = base / "endpoint_security" / "requirements.txt"
    dependency_report = check_requirements(requirements)
    checks.append({
        "name": "dependency_declarations",
        "status": dependency_report.get("status", "ERROR"),
        "report": dependency_report,
    })

    if tls_host is not None:
        if not HOST_RE.fullmatch(tls_host):
            raise ValueError("TLS host must be a hostname only, without URL, path, or credentials.")
        if not 1 <= tls_port <= 65535:
            raise ValueError("TLS port must be between 1 and 65535.")
        tls_report = check_tls_certificate(tls_host, port=tls_port)
        checks.append({
            "name": "explicit_tls_certificate",
            "status": tls_report.get("status", "REVIEW_REQUIRED"),
            "report": tls_report,
        })

    passed = sum(item["status"] == "PASS" for item in checks)
    review = sum(item["status"] == "REVIEW_REQUIRED" for item in checks)
    errors = sum(item["status"] == "ERROR" for item in checks)
    return {
        "project": "Tamanna AI",
        "component": "Cyber Security Center",
        "mode": "read_only",
        "network_checks_requested": tls_host is not None,
        "summary": {
            "total": len(checks),
            "passed": passed,
            "review_required": review,
            "errors": errors,
            "status": "PASS" if passed == len(checks) else "REVIEW_REQUIRED",
        },
        "checks": checks,
        "limitations": [
            "Repository checks do not certify the live application or VPS.",
            "The optional TLS check contacts only the explicitly named host and port.",
            "No port scan, exploit, brute force, file deletion, quarantine, or remediation is performed.",
            "Dependency declaration checks do not identify known vulnerable package versions.",
            "A passing report is not a penetration-test certification.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Tamanna AI's read-only Cyber Security Center.")
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="Local repository root.")
    parser.add_argument("--tls-host", help="Optional explicitly authorized TLS hostname (not a URL).")
    parser.add_argument("--tls-port", type=int, default=443, help="TLS port (default: 443).")
    args = parser.parse_args()
    try:
        report = run_center(args.root, args.tls_host, args.tls_port)
    except ValueError as exc:
        parser.error(str(exc))
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report["summary"]["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
