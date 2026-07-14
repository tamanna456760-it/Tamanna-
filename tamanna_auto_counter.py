#!/usr/bin/env python3

import json
from pathlib import Path
from datetime import datetime


class TamannaAutoCounter:
    def __init__(self, log_file="system.log"):
        self.log_file = Path(log_file)

        self.keywords = [
            "ERROR",
            "FAILED",
            "UNAUTHORIZED",
            "WARNING"
        ]

    def analyze(self):
        result = {
            "timestamp": datetime.now().isoformat(),
            "status": "ok",
            "alerts": []
        }

        if not self.log_file.exists():
            result["status"] = "log_not_found"
            return result

        with open(self.log_file, "r", encoding="utf-8", errors="ignore") as f:
            for line_no, line in enumerate(f, start=1):
                text = line.upper()

                for keyword in self.keywords:
                    if keyword in text:
                        result["alerts"].append({
                            "line": line_no,
                            "keyword": keyword,
                            "text": line.strip()
                        })

        if result["alerts"]:
            result["status"] = "attention_required"

        return result

    def save(self):
        report = self.analyze()

        with open("counter_report.json", "w", encoding="utf-8") as f:
            json.dump(report, f, indent=4)

        return report


if __name__ == "__main__":
    counter = TamannaAutoCounter()
    report = counter.save()

    print("=" * 50)
    print("Tamanna Auto Counter")
    print("=" * 50)
    print(json.dumps(report, indent=4))
    print("\nReport saved to counter_report.json")
