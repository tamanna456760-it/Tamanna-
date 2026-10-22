"""Unit tests for Tamanna AI audit report verification.
Owner: HM INSAN ALI
"""
import json
import tempfile
import unittest
from pathlib import Path
from endpoint_security.audit_report_verifier import verify_report
class TestAuditReportVerifier(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.report_path = Path(self.temp_dir.name) / "audit.json"
        self.report = {
            "project": "Tamanna AI",
            "owner": "HM INSAN ALI",
            "mode": "read_only",
            "summary": {
                "total": 1,
                "passed": 1,
                "failed": 0,
                "errors": 0,
                "overall_status": "PASS",
            },
            "checks": [
                {
                    "check": "configuration",
                    "status": "PASS",
                    "details": {"valid": True},
                }
            ],
        }
    def tearDown(self):
        self.temp_dir.cleanup()
    def write_report(self):
        self.report_path.write_text(
            json.dumps(self.report),
            encoding="utf-8",
        )
    def test_valid_report_passes(self):
        self.write_report()
        result = verify_report(self.report_path)
        self.assertTrue(result["valid"], result)
        self.assertEqual(result["checks_verified"], 1)
    def test_incorrect_summary_is_rejected(self):
        self.report["summary"]["passed"] = 0
        self.write_report()
        result = verify_report(self.report_path)
        self.assertFalse(result["valid"])
        self.assertTrue(result["errors"])
    def test_invalid_check_status_is_rejected(self):
        self.report["checks"][0]["status"] = "UNKNOWN"
        self.write_report()
        result = verify_report(self.report_path)
        self.assertFalse(result["valid"])
    def test_wrong_project_is_rejected(self):
        self.report["project"] = "Other Project"
        self.write_report()
        result = verify_report(self.report_path)
        self.assertFalse(result["valid"])
    def test_invalid_json_is_rejected(self):
        self.report_path.write_text(
            '{"project": "Tamanna AI",',
            encoding="utf-8",
        )
        result = verify_report(self.report_path)
        self.assertFalse(result["valid"])
        self.assertTrue(result["errors"])
    def test_missing_file_is_rejected(self):
        result = verify_report(
            Path(self.temp_dir.name) / "missing.json"
        )
        self.assertFalse(result["valid"])
    def test_failed_check_cannot_claim_overall_pass(self):
        self.report["checks"][0]["status"] = "FAIL"
        self.report["summary"].update({
            "passed": 0,
            "failed": 1,
            "overall_status": "PASS",
        })
        self.write_report()
        result = verify_report(self.report_path)
        self.assertFalse(result["valid"])
if __name__ == "__main__":
    unittest.main(verbosity=2)