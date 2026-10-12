"""
Tamanna AI Firewall - Security Summary Tests
Owner: HM INSAN ALI
"""
import json
import tempfile
import unittest
from pathlib import Path
from firewall.security_summary import (
    build_security_summary,
    save_security_summary,
)
def make_report(total=3, high_risk=1):
    return {
        "project": "Tamanna AI",
        "owner": "HM INSAN ALI",
        "generated_at": "2026-10-12T12:00:00+00:00",
        "analysis": {
            "total_events": total,
            "high_risk_events": high_risk,
        },
        "system_firewall_modified": False,
    }
class TestSecuritySummary(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.root = Path(self.temp_dir.name)
        self.report_path = self.root / "event_report.json"
        self.output_path = self.root / "reports" / "security_summary.json"
    def write_report(self, report):
        self.report_path.write_text(
            json.dumps(report),
            encoding="utf-8",
        )
    def test_high_risk_report_requires_review(self):
        self.write_report(make_report(total=3, high_risk=1))
        summary = build_security_summary(self.report_path)
        self.assertTrue(summary["report_valid"])
        self.assertEqual(summary["total_events"], 3)
        self.assertEqual(summary["high_risk_events"], 1)
        self.assertEqual(summary["status"], "REVIEW_REQUIRED")
    def test_no_high_risk_events(self):
        self.write_report(make_report(total=4, high_risk=0))
        summary = build_security_summary(self.report_path)
        self.assertEqual(
            summary["status"],
            "NO_HIGH_RISK_EVENTS_REPORTED",
        )
        self.assertEqual(summary["high_risk_events"], 0)
    def test_missing_report_is_handled(self):
        summary = build_security_summary(self.report_path)
        self.assertFalse(summary["report_available"])
        self.assertFalse(summary["report_valid"])
        self.assertEqual(
            summary["status"],
            "REPORT_INVALID_OR_UNAVAILABLE",
        )
    def test_invalid_json_is_handled(self):
        self.report_path.write_text(
            "{invalid json",
            encoding="utf-8",
        )
        summary = build_security_summary(self.report_path)
        self.assertFalse(summary["report_valid"])
        self.assertEqual(
            summary["status"],
            "REPORT_INVALID_OR_UNAVAILABLE",
        )
    def test_summary_is_saved_as_json(self):
        self.write_report(make_report(total=2, high_risk=0))
        result = save_security_summary(
            self.report_path,
            self.output_path,
        )
        self.assertTrue(self.output_path.is_file())
        saved = json.loads(
            self.output_path.read_text(encoding="utf-8")
        )
        self.assertEqual(saved["project"], "Tamanna AI")
        self.assertEqual(saved["total_events"], 2)
        self.assertEqual(result["status"], saved["status"])
    def test_summary_does_not_claim_to_modify_firewall(self):
        self.write_report(make_report())
        summary = build_security_summary(self.report_path)
        self.assertFalse(summary["system_firewall_modified"])
    def test_invalid_report_is_not_used_for_event_counts(self):
        self.write_report({
            "project": "Tamanna AI",
            "owner": "HM INSAN ALI",
        })
        summary = build_security_summary(self.report_path)
        self.assertFalse(summary["report_valid"])
        self.assertIsNone(summary["total_events"])
        self.assertIsNone(summary["high_risk_events"])
if __name__ == "__main__":
    unittest.main(verbosity=2)