# src/core/monitoring_system.py
import asyncio
import logging
from datetime import datetime

import psutil


class MonitoringSystem:
    """System health and performance monitoring"""

    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.metrics = {
            "cpu_usage": [],
            "memory_usage": [],
            "disk_usage": [],
            "network_io": [],
            "build_times": [],
        }

    async def start(self):
        """Start monitoring system"""
        self.logger.info("Starting Monitoring System...")

        # Start metric collection
        asyncio.create_task(self._collect_system_metrics())
        asyncio.create_task(self._collect_build_metrics())

        self.logger.info("Monitoring System started successfully")
        return True

    async def _collect_system_metrics(self):
        """Collect system performance metrics"""
        while True:
            try:
                # CPU usage
                cpu_percent = psutil.cpu_percent(interval=1)
                self.metrics["cpu_usage"].append(
                    {"timestamp": datetime.now(), "value": cpu_percent}
                )

                # Memory usage
                memory = psutil.virtual_memory()
                self.metrics["memory_usage"].append(
                    {"timestamp": datetime.now(), "value": memory.percent}
                )

                # Keep only last hour of data
                self._cleanup_old_metrics()

                await asyncio.sleep(30)  # Collect every 30 seconds

            except Exception as e:
                self.logger.error(f"Error collecting system metrics: {e}")
                await asyncio.sleep(60)
