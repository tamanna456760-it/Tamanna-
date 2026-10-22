#!/usr/bin/env python3
"""
Tamanna AI — Deployment Preflight Checker
Owner: HM INSAN ALI
Read-only pre-deployment checks.
Does not deploy, restart, or modify services.
"""
import argparse
import json
import shutil
import subprocess
from pathlib import Path
PROJECT = "Tamanna AI"
OWNER = "HM INSAN ALI"
def run_check(command):
    """Run a read-only validation command."""
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        return {
            "passed": result.returncode == 0,
            "return_code": result.returncode,
            "output": (result.stdout + result.stderr).strip()[-3000:],
        }
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {
            "passed": False,
            "return_code": None,
            "output": str(exc),
        }
def deployment_preflight(compose_file):
    findings = []
    checks = {}
    compose_path = Path(compose_file)
    if not compose_path.is_file():
        return {
            "project": PROJECT,
            "owner": OWNER,
            "status": "REVIEW_REQUIRED",
            "checks": {},
            "findings": [f"Compose file not found: {compose_path}"],
            "read_only": True,
        }
    docker = shutil.which("docker")
    if not docker:
        findings.append("Docker CLI is not installed or not in PATH.")
    else:
        checks["docker_version"] = run_check(
            [docker, "--version"]
        )
        checks["compose_config"] = run_check(
            [
                docker,
                "compose",
                "-f",
                str(compose_path),
                "config",
                "--quiet",
            ]
        )
        if not checks["compose_config"]["passed"]:
            findings.append("Docker Compose configuration validation failed.")
    return {
        "project": PROJECT,
        "owner": OWNER,
        "status": "PASS" if not findings else "REVIEW_REQUIRED",
        "checks": checks,
        "findings": findings,
        "read_only": True,
        "note": (
            "Runs Docker version and Compose configuration checks only. "
            "Does not build, deploy, or verify live HTTPS."
        ),
    }
def main():
    parser = argparse.ArgumentParser(
        description="Run Tamanna AI deployment preflight checks."
    )
    parser.add_argument(
        "--compose",
        default="deploy/docker-compose.yml",
        help="Path to Docker Compose file",
    )
    args = parser.parse_args()
    report = deployment_preflight(args.compose)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    raise SystemExit(0 if report["status"] == "PASS" else 1)
if __name__ == "__main__":
    main()