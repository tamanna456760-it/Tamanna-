File: ids/tests/test_ids_report.py

"""Tests for the Tamanna AI IDS report generator."""
import unittest
from ids.ids_manager import IDSManager
from ids.ids_report import generate_report
class TestIDSReport(unittest.TestCase):
    def setUp(self):
        self.manager = IDSManager(
            enabled=True,
            mode="monitor_only",
            minimum_severity="low",
        )
    def test_report_returns_dictionary(self):
        report = generate_report(self.manager)
        self.assertIsInstance(report, dict)
    def test_report_contains_project_metadata(self):
        report = generate_report(self.manager)
        self.assertEqual(report["project"], "Tamanna AI")
        self.assertEqual(report["owner"], "HM INSAN ALI")
    def test_report_contains_generation_timestamp(self):
        report = generate_report(self.manager)
        self.assertTrue(report["generated_at"])
    def test_report_contains_health_status(self):
        report = generate_report(self.manager)
        self.assertIn(
            report["health_status"],
            ("healthy", "degraded"),
        )
        self.assertIn("health_check", report)
    def test_report_counts_events(self):
        self.manager.record_event({"type": "test_one"})
        self.manager.record_event({"type": "test_two"})
        report = generate_report(self.manager)
        self.assertEqual(
            report["events"]["stored_in_memory"],
            2,
        )
    def test_report_includes_alert_summary(self):
        report = generate_report(self.manager)
        self.assertIsInstance(report["alerts"], dict)
    def test_report_shows_monitor_only_enforcement(self):
        report = generate_report(self.manager)
        enforcement = report["enforcement"]
        self.assertEqual(enforcement["mode"], "monitor_only")
        self.assertFalse(enforcement["automatic_ip_blocking"])
        self.assertFalse(enforcement["system_firewall_modified"])
    def test_report_uses_supplied_manager(self):
        manager = IDSManager(enabled=False)
        report = generate_report(manager)
        self.assertFalse(report["enabled"])
        self.assertEqual(report["mode"], "monitor_only")
    def test_report_does_not_modify_event_count(self):
        self.manager.record_event({"type": "before_report"})
        count_before = self.manager.collector.count()
        generate_report(self.manager)
        self.assertEqual(
            self.manager.collector.count(),
            count_before,
        )
if __name__ == "__main__":
    unittest.main()