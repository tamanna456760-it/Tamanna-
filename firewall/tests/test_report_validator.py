"""
Tamanna AI Firewall - Report Validator Tests
Owner: HM INSAN ALI
"""
import json
import tempfile
import unittest
from pathlib import Path
from firewall.report_validator import (
    validate_report,
    validate_report_file,
)
def make_valid_report():
    return {
        "project": "Tamanna AI",
        "owner": "HM INSAN ALI",
        "generated_at": "2026-10-12T12:00:00Z",
        "analysis": {
            "total_events": 3,
            "high_risk_events": 1,
        },
        "system_firewall_modified": False,
    }
class TestReportValidator(unittest.TestCase):
    def test_valid_report(self):
        result = validate_report(make_valid_report())
        self.assertTrue(result["valid"])
        self.assertEqual(result["errors"], [])
    def test_non_dictionary_report_is_rejected(self):
        result = validate_report(["not", "an", "object"])
        self.assertFalse(result["valid"])
        self.assertTrue(result["errors"])
    def test_missing_required_field_is_rejected(self):
        report = make_valid_report()
        del report["owner"]
        result = validate_report(report)
        self.assertFalse(result["valid"])
        self.assertTrue(
            any("owner" in error for error in result["errors"])
        )
    def test_wrong_project_name_is_rejected(self):
        report = make_valid_report()
        report["project"] = "Other Project"
        self.assertFalse(validate_report(report)["valid"])
    def test_negative_event_count_is_rejected(self):
        report = make_valid_report()
        report["analysis"]["total_events"] = -1
        self.assertFalse(validate_report(report)["valid"])
    def test_high_risk_count_cannot_exceed_total(self):
        report = make_valid_report()
        report["analysis"]["high_risk_events"] = 4
        self.assertFalse(validate_report(report)["valid"])
    def test_boolean_is_not_accepted_as_event_count(self):
        report = make_valid_report()
        report["analysis"]["total_events"] = True
        self.assertFalse(validate_report(report)["valid"])
    def test_firewall_status_must_be_boolean(self):
        report = make_valid_report()
        report["system_firewall_modified"] = "false"
        self.assertFalse(validate_report(report)["valid"])
    def test_valid_report_file(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "report.json"
            path.write_text(
                json.dumps(make_valid_report()),
                encoding="utf-8",
            )
            result = validate_report_file(path)
            self.assertTrue(result["valid"])
    def test_missing_report_file(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "missing.json"
            result = validate_report_file(path)
            self.assertFalse(result["valid"])
            self.assertTrue(
                any("not found" in error for error in result["errors"])
            )
    def test_invalid_json_file(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "broken.json"
            path.write_text("{invalid json", encoding="utf-8")
            result = validate_report_file(path)
            self.assertFalse(result["valid"])
            self.assertTrue(result["errors"])
if __name__ == "__main__":
    unittest.main(verbosity=2)