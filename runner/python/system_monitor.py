# System monitoring for security
import logging

import psutil


class SystemMonitor:
    def __init__(self):
        self.logger = logging.getLogger("SystemMonitor")

    def monitor_services(self):
        """Monitor running services"""
        services = []
        for proc in psutil.process_iter(["pid", "name", "status"]):
            services.append(proc.info)
        return services

    def check_system_health(self):
        """Check system resource usage"""
        return {
            "cpu_percent": psutil.cpu_percent(),
            "memory_usage": psutil.virtual_memory().percent,
            "disk_usage": psutil.disk_usage("/").percent,
        }
