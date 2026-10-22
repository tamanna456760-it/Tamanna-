#!/usr/bin/env python3
"""
Tamanna AI — TLS Security Policy Checker
Owner: HM INSAN ALI
Read-only evaluation of a TLS inspection report.
This tool does not connect to the server itself.
"""
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
PROJECT = "Tamanna AI"
OWNER = "HM INSAN ALI"
APPROVED_TLS_VERSIONS = {"TLSv1.2", "TLSv1.3"}
MINIMUM_REMAINING_DAYS = 30
def evaluate_tls_report(report):
    findings = []
    if not isinstance(report, dict):
        report = {}
        findings.append("Input must be a JSON object.")
    if report.get("project") != PROJECT:
        findings.append("Project identity mismatch.")
    if report.get("owner") != OWNER:
        findings.append("Owner identity mismatch.")
    tls_version = report.get("tls_version")
    if tls_version not in APPROVED_TLS_VERSIONS:
        findings.append("TLS version is missing or not approved.")
    expiry = report.get("certificate_expires_utc")
    if not isinstance(expiry, str):
        findings.append("Certificate expiry timestamp is missing.")
    else:
        try:
            expires_at = datetime.fromisoformat(
                expiry.replace("Z", "+00:00")
            )
            if expires_at.tzinfo is None:
                findings.append(
                    "Certificate expiry timestamp must include timezone."
                )
            else:
                days_left = (
                    expires_at.astimezone(timezone.utc)
                    - datetime.now(timezone.utc)
                ).total_seconds() / 86400
                if days_left <= 0:
                    findings.append("Certificate has expired.")
                elif days_left < MINIMUM_REMAINING_DAYS:
                    findings.append(
                        "Certificate expires in fewer than 30 days."
                    )
        except ValueError:
            findings.append("Certificate expiry timestamp is invalid.")
    return {
        "project": PROJECT,
        "owner": OWNER,
        "status": "PASS" if not findings else "REVIEW_REQUIRED",
        "findings": findings,
        "read_only": True,
        "note": (
            "Evaluates supplied report fields only; does not independently "
            "verify the remote server or authenticate the report."
        ),
    }
def main():
    parser = argparse.ArgumentParser(
        description="Evaluate a Tamanna AI TLS report JSON file."
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Path to a TLS inspection report JSON file",
    )
    args = parser.parse_args()
    try:
        with Path(args.input).open("r", encoding="utf-8") as file:
            report = json.load(file)
    except (OSError, json.JSONDecodeError, UnicodeError) as exc:
        print(json.dumps({
            "project": PROJECT,
            "owner": OWNER,
            "status": "REVIEW_REQUIRED",
            "findings": [f"Cannot read input report: {exc}"],
            "read_only": True,
        }, indent=2))
        raise SystemExit(1)
    result = evaluate_tls_report(report)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    raise SystemExit(0 if result["status"] == "PASS" else 1)
if __name__ == "__main__":
    main()