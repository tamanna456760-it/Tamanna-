#!/usr/bin/env python3

import json
import platform
import socket
from datetime import datetime

try:
    import psutil
except ImportError:
    print("psutil is not installed.")
    print("Install with: pip install psutil")
    raise SystemExit(1)


class AISystemMonitor:
    def __init__(self):
        self.start_time = datetime.now()

    def get_system_info(self):
        return {
            "hostname": socket.gethostname(),
            "platform": platform.system(),
            "platform_version": platform.version(),
            "python_version": platform.python_version(),
        }

    def get_cpu(self):
        return {
            "usage_percent": psutil.cpu_percent(interval=1),
            "cores": psutil.cpu_count(),
        }

    def get_memory(self):
        mem = psutil.virtual_memory()
        return {
            "total_mb": round(mem.total / 1024 / 1024, 2),
            "used_mb": round(mem.used / 1024 / 1024, 2),
            "percent": mem.percent,
        }

    def get_disk(self):
        disk = psutil.disk_usage("/")
        return {
            "total_gb": round(disk.total / 1024**3, 2),
            "used_gb": round(disk.used / 1024**3, 2),
            "free_gb": round(disk.free / 1024**3, 2),
            "percent": disk.percent,
        }

    def generate_report(self):
        report = {
            "timestamp": datetime.now().isoformat(),
            "system": self.get_system_info(),
            "cpu": self.get_cpu(),
            "memory": self.get_memory(),
            "disk": self.get_disk(),
        }

        with open("system_report.json", "w", encoding="utf-8") as f:
            json.dump(report, f, indent=4)

        return report


if __name__ == "__main__":
    monitor = AISystemMonitor()
    report = monitor.generate_report()

    print("=" * 50)
    print("Tamanna AI System Monitor")
    print("=" * 50)
    print(json.dumps(report, indent=4))
    print("\nReport saved to system_report.json")
