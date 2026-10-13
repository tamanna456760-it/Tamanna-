#!/usr/bin/env python3
"""Tests for Tamanna AI security posture report verifier.
Owner: HM INSAN ALI
Uses temporary test files only.
"""
from __future__ import annotations
import json
import tempfile
import unittest
from pathlib import Path
from endpoint_security.security_posture_verifier import (
    verify_posture_report,
)
class TestSecurityPostureVerifier(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.report_path = Path(self.temp_dir.name) / "posture.json"
    def write_report(self, report: object) -> None:
        self.report_path.write_text(
            json.dumps(report),
            encoding="utf-8",
        )
    @staticmethod
    def valid_report() -> dict:
        return {
            "project": "Tamanna AI",
            "owner": "HM INSAN ALI",
            "generated_at_utc": "2026-10-12T10:00:00+00:00",
            "checks": [
                {"name": "configuration", "status": "PASS"},
                {"name": "logging", "status": "PASS"},
            ],
            "checks_passed": 2,
            "checks_failed": 0,
            "checks_error": 0,
        }
    def test_valid_report_passes(self) -> None:
        self.write_report(self.valid_report())
        result = verify_posture_report(self.report_path)
        self.assertTrue(result["valid"])
        self.assertEqual(result["status"], "VALID")
        self.assertEqual(result["checks_total"], 2)
        self.assertEqual(result["checks_passed"], 2)
    def test_failed_check_requires_review(self) -> None:
        report = self.valid_report()
        report["checks"][0]["status"] = "FAIL"
        report["checks_passed"] = 1
        report["checks_failed"] = 1
        self.write_report(report)
        result = verify_posture_report(self.report_path)
        self.assertTrue(result["valid"])
        self.assertEqual(result["status"], "REVIEW_REQUIRED")
        self.assertEqual(result["checks_failed"], 1)
    def test_incorrect_summary_is_invalid(self) -> None:
        report = self.valid_report()
        report["checks_passed"] = 99
        self.write_report(report)
        result = verify_posture_report(self.report_path)
        self.assertFalse(result["valid"])
        self.assertEqual(result["status"], "INVALID")
        self.assertTrue(result["errors"])
    def test_wrong_project_is_invalid(self) -> None:
        report = self.valid_report()
        report["project"] = "Other Project"
        self.write_report(report)
        result = verify_posture_report(self.report_path)
        self.assertFalse(result["valid"])
        self.assertEqual(result["status"], "INVALID")
    def test_missing_timestamp_is_invalid(self) -> None:
        report = self.valid_report()
        del report["generated_at_utc"]
        self.write_report(report)
        result = verify_posture_report(self.report_path)
        self.assertFalse(result["valid"])
        self.assertIn(
            "Missing generated_at_utc timestamp.",
            result["errors"],
        )
    def test_unknown_check_status_is_invalid(self) -> None:
        report = self.valid_report()
        report["checks"][0]["status"] = "MAYBE"
        report["checks_error"] = 1
        report["checks_passed"] = 1
        self.write_report(report)
        result = verify_posture_report(self.report_path)
        self.assertFalse(result["valid"])
        self.assertEqual(result["status"], "INVALID")
    def test_invalid_json_returns_error(self) -> None:
        self.report_path.write_text("{broken", encoding="utf-8")
        result = verify_posture_report(self.report_path)
        self.assertFalse(result["valid"])
        self.assertEqual(result["status"], "ERROR")
    def test_missing_file_returns_error(self) -> None:
        result = verify_posture_report(self.report_path)
        self.assertFalse(result["valid"])
        self.assertEqual(result["status"], "ERROR")
    def test_non_object_json_is_invalid(self) -> None:
        self.report_path.write_text("[]", encoding="utf-8")
        result = verify_posture_report(self.report_path)
        self.assertFalse(result["valid"])
        self.assertEqual(result["status"], "INVALID")
if __name__ == "__main__":
    unittest.main(verbosity=2)