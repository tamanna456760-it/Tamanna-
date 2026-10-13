#!/usr/bin/env python3
"""Tests for Tamanna AI security posture reporting.
Owner: HM INSAN ALI
These tests use temporary files and do not modify real audit reports.
"""
from __future__ import annotations
import json
import tempfile
import unittest
from pathlib import Path
from endpoint_security.security_posture_report import summarize_reports
class TestSecurityPostureReport(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.report_dir = Path(self.temp_dir.name)
    def write_report(self, name: str, report: dict) -> Path:
        path = self.report_dir / name
        path.write_text(
            json.dumps(report),
            encoding="utf-8",
        )
        return path
    def test_missing_directory_is_reported(self) -> None:
        missing_dir = self.report_dir / "missing"
        result = summarize_reports(missing_dir)
        self.assertEqual(result["status"], "REPORT_DIRECTORY_MISSING")
        self.assertEqual(result["reports_found"], 0)
        self.assertTrue(result["read_only"])
    def test_empty_directory_has_no_reports(self) -> None:
        result = summarize_reports(self.report_dir)
        self.assertEqual(result["status"], "NO_REPORTS")
        self.assertEqual(result["reports_found"], 0)
        self.assertEqual(result["reports_read"], 0)
    def test_valid_report_is_counted(self) -> None:
        self.write_report(
            "audit.json",
            {
                "project": "Tamanna AI",
                "owner": "HM INSAN ALI",
                "status": "PASS",
                "audit_time_utc": "2026-10-12T10:00:00+00:00",
                "summary": {"passed": 1, "failed": 0},
                "checks": [
                    {"name": "config", "status": "PASS"},
                    {"name": "logging", "status": "PASS"},
                ],
            },
        )
        result = summarize_reports(self.report_dir)
        self.assertEqual(result["status"], "REPORTS_READ")
        self.assertEqual(result["reports_read"], 1)
        self.assertEqual(result["checks_passed"], 2)
        self.assertEqual(result["checks_failed"], 0)
    def test_failed_check_requires_review(self) -> None:
        self.write_report(
            "audit.json",
            {
                "project": "Tamanna AI",
                "status": "FAIL",
                "checks": [
                    {"name": "policy", "status": "FAIL"},
                ],
            },
        )
        result = summarize_reports(self.report_dir)
        self.assertEqual(result["status"], "REVIEW_REQUIRED")
        self.assertEqual(result["checks_failed"], 1)
    def test_invalid_json_is_counted(self) -> None:
        (self.report_dir / "broken.json").write_text(
            "{invalid",
            encoding="utf-8",
        )
        result = summarize_reports(self.report_dir)
        self.assertEqual(result["status"], "REVIEW_REQUIRED")
        self.assertEqual(result["reports_invalid"], 1)
        self.assertEqual(result["reports"][0]["status"], "INVALID")
    def test_wrong_project_is_rejected(self) -> None:
        self.write_report(
            "other.json",
            {
                "project": "Different Project",
                "status": "PASS",
                "checks": [],
            },
        )
        result = summarize_reports(self.report_dir)
        self.assertEqual(result["reports_invalid"], 1)
        self.assertEqual(result["status"], "REVIEW_REQUIRED")
    def test_non_object_json_is_rejected(self) -> None:
        (self.report_dir / "array.json").write_text(
            "[]",
            encoding="utf-8",
        )
        result = summarize_reports(self.report_dir)
        self.assertEqual(result["reports_invalid"], 1)
        self.assertEqual(result["status"], "REVIEW_REQUIRED")
    def test_unknown_check_status_counts_as_error(self) -> None:
        self.write_report(
            "audit.json",
            {
                "project": "Tamanna AI",
                "status": "UNKNOWN",
                "checks": [
                    {"name": "dependency", "status": "UNKNOWN"},
                ],
            },
        )
        result = summarize_reports(self.report_dir)
        self.assertEqual(result["checks_error"], 1)
        self.assertEqual(result["status"], "REVIEW_REQUIRED")
if __name__ == "__main__":
    unittest.main(verbosity=2)