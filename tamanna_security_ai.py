#!/usr/bin/env python3

import json
import os
import stat
from pathlib import Path
from datetime import datetime


class TamannaSecurityAI:
    def __init__(self):
        self.project_root = Path(__file__).parent

    def check_env_file(self):
        env = self.project_root / ".env"
        return {
            "exists": env.exists(),
            "recommendation": (
                "Keep .env out of version control."
                if env.exists()
                else "Create a .env file for secrets if needed."
            ),
        }

    def check_world_writable_files(self):
        findings = []

        for file in self.project_root.rglob("*"):
            if not file.is_file():
                continue

            try:
                mode = file.stat().st_mode
                if mode & stat.S_IWOTH:
                    findings.append(str(file.relative_to(self.project_root)))
            except OSError:
                pass

        return findings

    def check_common_passwords(self):
        config = self.project_root / "users.json"

        if not config.exists():
            return []

        weak = {
            "123456",
            "password",
            "admin",
            "qwerty",
        }

        findings = []

        try:
            users = json.loads(config.read_text())

            for user in users:
                if user.get("password") in weak:
                    findings.append(user.get("username"))
        except Exception:
            pass

        return findings

    def generate_report(self):
        report = {
            "timestamp": datetime.now().isoformat(),
            "checks": {
                "env": self.check_env_file(),
                "world_writable_files": self.check_world_writable_files(),
                "weak_passwords": self.check_common_passwords(),
            },
        }

        with open("security_report.json", "w") as f:
            json.dump(report, f, indent=4)

        return report


if __name__ == "__main__":
    security = TamannaSecurityAI()
    report = security.generate_report()

    print("=" * 50)
    print("Tamanna Security AI")
    print("=" * 50)
    print(json.dumps(report, indent=4))
    print("\nReport saved to security_report.json")
