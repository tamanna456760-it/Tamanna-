# system_monitor.py - Legitimate system monitoring
import json
import logging
import time
from datetime import datetime

import psutil


class SystemMonitor:
    """Monitor system resources for legitimate purposes"""

    def __init__(self, log_file="system_monitor.log"):
        self.log_file = log_file
        logging.basicConfig(
            filename=log_file,
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
        )

    def get_system_health(self):
        """Monitor system health metrics"""
        try:
            metrics = {
                "timestamp": datetime.now().isoformat(),
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory_usage": dict(psutil.virtual_memory()._asdict()),
                "disk_usage": dict(psutil.disk_usage("/")._asdict()),
                "network_io": dict(psutil.net_io_counters()._asdict()),
                "running_processes": len(psutil.pprocess_ids()),
            }
            return metrics
        except Exception as e:
            logging.error(f"Error collecting system metrics: {e}")
            return None

    def monitor_continuously(self, interval=60):
        """Continuous monitoring with specified interval"""
        print(f"Starting system monitoring (interval: {interval}s)")
        while True:
            try:
                metrics = self.get_system_health()
                if metrics:
                    logging.info(f"System metrics: {json.dumps(metrics)}")
                    print(
                        f"CPU: {metrics['cpu_percent']}% | "
                        f"Memory: {metrics['memory_usage']['percent']}%"
                    )

                time.sleep(interval)
            except KeyboardInterrupt:
                print("\nMonitoring stopped by user")
                break
            except Exception as e:
                logging.error(f"Monitoring error: {e}")
                time.sleep(interval)


# Usage for legitimate system administration
if __name__ == "__main__":
    monitor = SystemMonitor()
    monitor.monitor_continuously(interval=30)
