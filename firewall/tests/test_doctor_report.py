"""
Tamanna AI Firewall - Doctor Report Tests
Owner: HM INSAN ALI
"""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from firewall.doctor_report import (
    generate_doctor_report,
    save_doctor_report,
)
class TestDoctorReport(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.root = Path(self.temp_dir.name)
        self.output_path = self.root / "reports" / "doctor_report.json"
    @patch("firewall.doctor_report.run_diagnostics")
    def test_generate_report_contains_diagnostics(self, mock_diagnostics):
        mock_diagnostics.return_value = {
            "project": "Tamanna AI",
            "owner": "HM INSAN ALI",
            "status": "OK",
            "checks_passed": 5,
            "checks_failed": 0,
            "errors": [],
        }
        report = generate_doctor_report(self.root)
        self.assertEqual(report["project"], "Tamanna AI")
        self.assertEqual(report["owner"], "HM INSAN ALI")
        self.assertEqual(
            report["diagnostics"]["status"],
            "OK",
        )
        self.assertFalse(report["system_firewall_modified"])
    @patch("firewall.doctor_report.run_diagnostics")
    def test_save_report_creates_json_file(self, mock_diagnostics):
        mock_diagnostics.return_value = {
            "status": "OK",
            "checks_passed": 5,
            "checks_failed": 0,
            "errors": [],
        }
        result = save_doctor_report(self.output_path, self.root)
        self.assertTrue(self.output_path.is_file())
        self.assertNotIn("save_error", result)
        saved = json.loads(
            self.output_path.read_text(encoding="utf-8")
        )
        self.assertEqual(saved["report_type"], "firewall_doctor")
        self.assertEqual(saved["diagnostics"]["status"], "OK")
    @patch("firewall.doctor_report.run_diagnostics")
    def test_failed_diagnostics_are_preserved(self, mock_diagnostics):
        mock_diagnostics.return_value = {
            "status": "ISSUES_FOUND",
            "checks_passed": 2,
            "checks_failed": 1,
            "errors": ["Missing required file"],
        }
        report = generate_doctor_report(self.root)
        self.assertEqual(
            report["diagnostics"]["status"],
            "ISSUES_FOUND",
        )
        self.assertEqual(
            report["diagnostics"]["checks_failed"],
            1,
        )
    @patch("firewall.doctor_report.run_diagnostics")
    def test_report_does_not_claim_firewall_changes(self, mock_diagnostics):
        mock_diagnostics.return_value = {
            "status": "OK",
            "checks_passed": 1,
            "checks_failed": 0,
            "errors": [],
        }
        report = generate_doctor_report(self.root)
        self.assertIs(
            report["system_firewall_modified"],
            False,
        )
    @patch("firewall.doctor_report.run_diagnostics")
    def test_output_directory_is_created(self, mock_diagnostics):
        mock_diagnostics.return_value = {
            "status": "OK",
            "checks_passed": 1,
            "checks_failed": 0,
            "errors": [],
        }
        self.assertFalse(self.output_path.parent.exists())
        save_doctor_report(self.output_path, self.root)
        self.assertTrue(self.output_path.parent.is_dir())
if __name__ == "__main__":
    unittest.main(verbosity=2)