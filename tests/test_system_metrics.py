import unittest
from unittest.mock import patch

from tamanna_ai.integrations import system_metrics


class SystemMetricsTests(unittest.IsolatedAsyncioTestCase):
    async def test_collects_cpu_memory_disk_and_gpu_metrics(self):
        disk = type("DiskUsage", (), {
            "used": 500, "total": 1000, "free": 500
        })()
        with patch.object(system_metrics, "_cpu_percent", return_value=42.5), patch.object(
            system_metrics, "_memory_bytes", return_value=(2000, 1000)
        ), patch.object(system_metrics, "_gpu_metrics", return_value={
            "available": False, "vendor": None, "utilization_percent": None,
            "memory_used_mb": None, "memory_total_mb": None, "name": None,
        }), patch.object(system_metrics.shutil, "disk_usage", return_value=disk):
            result = await system_metrics.collect_system_metrics()

        self.assertEqual(result["cpu"]["usage_percent"], 42.5)
        self.assertEqual(result["memory"]["usage_percent"], 50.0)
        self.assertEqual(result["disk"]["usage_percent"], 50.0)
        self.assertFalse(result["gpu"]["available"])
        self.assertGreaterEqual(result["cpu"]["logical_cores"] or 0, 1)


if __name__ == "__main__":
    unittest.main()
