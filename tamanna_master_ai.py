#!/usr/bin/env python3

import json
from datetime import datetime

try:
    from ai_brain_core import TamannaBrain
except ImportError:
    TamannaBrain = None

try:
    from ai_system_monitor import AISystemMonitor
except ImportError:
    AISystemMonitor = None


class TamannaMasterAI:
    def __init__(self):
        self.name = "Tamanna Master AI"
        self.version = "1.0.0"
        self.started = datetime.now().isoformat()

    def run(self):
        report = {
            "name": self.name,
            "version": self.version,
            "started": self.started,
            "modules": {}
        }

        if TamannaBrain:
            brain = TamannaBrain()
            report["modules"]["brain"] = brain.info()
        else:
            report["modules"]["brain"] = {
                "status": "Module not available"
            }

        if AISystemMonitor:
            monitor = AISystemMonitor()
            report["modules"]["system"] = monitor.generate_report()
        else:
            report["modules"]["system"] = {
                "status": "Module not available"
            }

        return report


if __name__ == "__main__":
    ai = TamannaMasterAI()
    report = ai.run()

    with open("master_ai_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=4)

    print("=" * 50)
    print("Tamanna Master AI")
    print("=" * 50)
    print(json.dumps(report, indent=4))
    print("\nReport saved to master_ai_report.json")
