"""
Tamanna AI Firewall - Event Report Tests
Owner: HM INSAN ALI
"""
import json
import tempfile
import unittest
from pathlib import Path
from firewall.event_report import generate_event_report
from firewall.security_event_store import SecurityEventStore
class TestEventReport(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        root = Path(self.temp_dir.name)
        self.event_path = root / "events.jsonl"
        self.report_path = root / "reports" / "event_report.json"
        self.store = SecurityEventStore(self.event_path)
    def test_report_is_created(self):
        self.store.append_event(
            event_type="login_failed",
            severity="HIGH",
            details={"client": "test-client"},
        )
        report = generate_event_report(
            report_path=self.report_path,
            event_store=self.store,
        )
        self.assertTrue(self.report_path.is_file())
        self.assertEqual(report["project"], "Tamanna AI")
        self.assertEqual(report["owner"], "HM INSAN ALI")
    def test_saved_json_matches_returned_report(self):
        self.store.append_event(
            event_type="request_received",
            severity="INFO",
        )
        report = generate_event_report(
            report_path=self.report_path,
            event_store=self.store,
        )
        saved = json.loads(
            self.report_path.read_text(encoding="utf-8")
        )
        self.assertEqual(saved, report)
        self.assertIn("generated_at", saved)
        self.assertIn("analysis", saved)
    def test_event_counts_are_included(self):
        self.store.append_event(
            event_type="login_failed",
            severity="HIGH",
        )
        self.store.append_event(
            event_type="request_received",
            severity="INFO",
        )
        report = generate_event_report(
            report_path=self.report_path,
            event_store=self.store,
        )
        analysis = report["analysis"]
        self.assertEqual(analysis["total_events"], 2)
        self.assertEqual(analysis["high_risk_events"], 1)
    def test_empty_store_generates_empty_summary(self):
        report = generate_event_report(
            report_path=self.report_path,
            event_store=self.store,
        )
        self.assertEqual(report["analysis"]["total_events"], 0)
        self.assertEqual(report["analysis"]["high_risk_events"], 0)
    def test_report_directory_is_created(self):
        self.assertFalse(self.report_path.parent.exists())
        generate_event_report(
            report_path=self.report_path,
            event_store=self.store,
        )
        self.assertTrue(self.report_path.parent.is_dir())
    def test_system_firewall_is_not_modified(self):
        report = generate_event_report(
            report_path=self.report_path,
            event_store=self.store,
        )
        self.assertFalse(report["system_firewall_modified"])
if __name__ == "__main__":
    unittest.main(verbosity=2)