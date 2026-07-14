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

try:
    from tamanna_master_ai import TamannaMasterAI
except ImportError:
    TamannaMasterAI = None


class TamannaHead:

    def __init__(self):
        self.system_name = "Tamanna Head"
        self.version = "1.0.0"
        self.started = datetime.now().isoformat()

    def get_status(self):

        status = {
            "system": self.system_name,
            "version": self.version,
            "started": self.started,
            "modules": {}
        }

        if TamannaBrain:
            try:
                brain = TamannaBrain()
                status["modules"]["brain"] = {
                    "loaded": True,
                    "status": brain.status()
                }
            except Exception as e:
                status["modules"]["brain"] = {
                    "loaded": False,
                    "error": str(e)
                }

        if AISystemMonitor:
            try:
                monitor = AISystemMonitor()
                status["modules"]["monitor"] = {
                    "loaded": True,
                    "report": monitor.generate_report()
                }
            except Exception as e:
                status["modules"]["monitor"] = {
                    "loaded": False,
                    "error": str(e)
                }

        if TamannaMasterAI:
            try:
                master = TamannaMasterAI()
                status["modules"]["master_ai"] = {
                    "loaded": True
                }
            except Exception as e:
                status["modules"]["master_ai"] = {
                    "loaded": False,
                    "error": str(e)
                }

        return status

    def save_report(self):
        report = self.get_status()

        with open("tamanna_head_report.json", "w") as f:
            json.dump(report, f, indent=4)

        return report


if __name__ == "__main__":

    head = TamannaHead()

    report = head.save_report()

    print("=" * 50)
    print("Tamanna Head")
    print("=" * 50)
    print(json.dumps(report, indent=4))
