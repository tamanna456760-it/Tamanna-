File: ids/tests/test_health_check.py

"""Tests for the Tamanna AI IDS health check."""
import unittest
from ids.health_check import run_health_check
from ids.ids_manager import IDSManager
class TestIDSHealthCheck(unittest.TestCase):
    def setUp(self):
        self.manager = IDSManager(
            enabled=True,
            mode="monitor_only",
        )
    def test_health_check_returns_dictionary(self):
        report = run_health_check(self.manager)
        self.assertIsInstance(report, dict)
    def test_health_check_contains_project_metadata(self):
        report = run_health_check(self.manager)
        self.assertEqual(report["project"], "Tamanna AI")
        self.assertEqual(report["owner"], "HM INSAN ALI")
    def test_health_check_contains_timestamp(self):
        report = run_health_check(self.manager)
        self.assertTrue(report["checked_at"])
    def test_health_check_contains_all_components(self):
        report = run_health_check(self.manager)
        self.assertIn("collector", report["components"])
        self.assertIn("detector", report["components"])
        self.assertIn("alerts", report["components"])
    def test_healthy_components_report_ok(self):
        report = run_health_check(self.manager)
        self.assertEqual(report["status"], "healthy")
        for component in report["components"].values():
            self.assertEqual(component["status"], "ok")
    def test_health_check_reports_monitor_only_mode(self):
        report = run_health_check(self.manager)
        self.assertEqual(report["mode"], "monitor_only")
        self.assertFalse(report["automatic_ip_blocking"])
        self.assertFalse(report["system_firewall_modified"])
    def test_health_check_uses_supplied_manager(self):
        manager = IDSManager(enabled=False)
        report = run_health_check(manager)
        self.assertFalse(report["enabled"])
        self.assertEqual(report["mode"], "monitor_only")
    def test_health_check_without_manager(self):
        report = run_health_check()
        self.assertIsInstance(report, dict)
        self.assertIn("components", report)
if __name__ == "__main__":
    unittest.main()