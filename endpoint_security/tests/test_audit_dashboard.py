"""Unit tests for Tamanna AI audit dashboard.
Owner: HM INSAN ALI
"""
import json
import tempfile
import unittest
from pathlib import Path
from endpoint_security.audit_dashboard import build_dashboard
class TestAuditDashboard(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.report_dir = Path(self.temp_dir.name)
    def tearDown(self):
        self.temp_dir.cleanup()
    def write_report(self, filename, audit_time, status="PASS"):
        report = {
            "project": "Tamanna AI",
            "owner": "HM INSAN ALI",
            "audit_time_utc": audit_time,
            "summary": {
                "total": 2,
                "passed": 2 if status == "PASS" else 1,
                "failed": 0 if status == "PASS" else 1,
                "errors": 0,
                "overall_status": status,
            },
            "checks": [],
        }
        (self.report_dir / filename).write_text(
            json.dumps(report),
            encoding="utf-8",
        )
    def test_empty_directory_returns_zero_reports(self):
        result = build_dashboard(self.report_dir)
        self.assertEqual(result["report_count"], 0)
        self.assertIsNone(result["latest_report"])
    def test_valid_report_is_counted(self):
        self.write_report("audit1.json", "2026-10-10T10:00:00+00:00")
        result = build_dashboard(self.report_dir)
        self.assertEqual(result["report_count"], 1)
        self.assertEqual(result["totals"]["passed"], 2)
    def test_latest_report_is_selected(self):
        self.write_report("old.json", "2026-10-09T10:00:00+00:00")
        self.write_report("new.json", "2026-10-10T10:00:00+00:00")
        result = build_dashboard(self.report_dir)
        self.assertEqual(
            result["latest_report"]["file"],
            "new.json",
        )
    def test_invalid_json_is_reported(self):
        (self.report_dir / "broken.json").write_text(
            '{"project": ',
            encoding="utf-8",
        )
        result = build_dashboard(self.report_dir)
        self.assertEqual(result["report_count"], 0)
        self.assertEqual(result["invalid_report_count"], 1)
    def test_wrong_project_is_rejected(self):
        (self.report_dir / "wrong.json").write_text(
            json.dumps({"project": "Other Project", "summary": {}}),
            encoding="utf-8",
        )
        result = build_dashboard(self.report_dir)
        self.assertEqual(result["report_count"], 0)
        self.assertEqual(result["invalid_report_count"], 1)
    def test_failed_report_contributes_to_totals(self):
        self.write_report(
            "failed.json",
            "2026-10-10T12:00:00+00:00",
            status="REVIEW_REQUIRED",
        )
        result = build_dashboard(self.report_dir)
        self.assertEqual(result["totals"]["failed"], 1)
        self.assertEqual(
            result["latest_report"]["overall_status"],
            "REVIEW_REQUIRED",
        )
if __name__ == "__main__":
    unittest.main(verbosity=2)