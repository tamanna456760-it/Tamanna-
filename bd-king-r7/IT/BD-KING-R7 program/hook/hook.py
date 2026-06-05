#!/usr/bin/env python3

import subprocess
import json
import os
from datetime import datetime

REPORT_FILE = "hook_report.json"


def run_command(cmd):
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True
        )

        return {
            "command": cmd,
            "return_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr
        }

    except Exception as e:
        return {
            "command": cmd,
            "error": str(e)
        }


def main():
    report = {
        "timestamp": datetime.utcnow().isoformat(),
        "checks": []
    }

    commands = [
        "ruff check .",
        "python -m compileall .",
        "git status --short"
    ]

    for cmd in commands:
        report["checks"].append(run_command(cmd))

    with open(REPORT_FILE, "w") as f:
        json.dump(report, f, indent=4)

    print(f"Hook completed. Report saved to {REPORT_FILE}")


if __name__ == "__main__":
    main()