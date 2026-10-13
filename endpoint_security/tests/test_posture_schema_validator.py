#!/usr/bin/env python3
"""Tests for the Tamanna AI posture schema validator.
Owner: HM INSAN ALI
All test files are temporary and isolated.
"""
from __future__ import annotations
import json
import tempfile
import unittest
from pathlib import Path
from endpoint_security.posture_schema_validator import (
    validate_posture_report,
)
SCHEMA_PATH = (
    Path(__file__).resolve().parents[1]
    / "security_posture_schema.json"
)
class TestPostureSchemaValidator(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.report_path = Path(self.temp_dir.name) / "report.json"
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
            "generated_at_utc": "2026-10-12T10:00:00Z",
            "status": "VALID",
            "checks": [
                {
                    "name": "configuration",
                    "status": "PASS",
                }
            ],
            "checks_passed": 1,
            "checks_failed": 0,
            "checks_error": 0,
            "read_only": True,
        }
    def test_valid_report_passes_schema(self) -> None:
        self.write_report(self.valid_report())
        result = validate_posture_report(
            self.report_path,
            SCHEMA_PATH,
        )
        self.assertTrue(result["valid"], result.get("errors"))
        self.assertEqual(result["status"], "VALID")
        self.assertEqual(result["error_count"], 0)
    def test_wrong_project_fails_validation(self) -> None:
        report = self.valid_report()
        report["project"] = "Other Project"
        self.write_report(report)
        result = validate_posture_report(
            self.report_path,
            SCHEMA_PATH,
        )
        self.assertFalse(result["valid"])
        self.assertEqual(result["status"], "INVALID")
    def test_missing_required_field_fails_validation(self) -> None:
        report = self.valid_report()
        del report["owner"]
        self.write_report(report)
        result = validate_posture_report(
            self.report_path,
            SCHEMA_PATH,
        )
        self.assertFalse(result["valid"])
        self.assertGreater(result["error_count"], 0)
    def test_invalid_timestamp_fails_validation(self) -> None:
        report = self.valid_report()
        report["generated_at_utc"] = "not-a-timestamp"
        self.write_report(report)
        result = validate_posture_report(
            self.report_path,
            SCHEMA_PATH,
        )
        self.assertFalse(result["valid"])
        self.assertEqual(result["status"], "INVALID")
    def test_read_only_must_be_true(self) -> None:
        report = self.valid_report()
        report["read_only"] = False
        self.write_report(report)
        result = validate_posture_report(
            self.report_path,
            SCHEMA_PATH,
        )
        self.assertFalse(result["valid"])
    def test_negative_count_fails_validation(self) -> None:
        report = self.valid_report()
        report["checks_passed"] = -1
        self.write_report(report)
        result = validate_posture_report(
            self.report_path,
            SCHEMA_PATH,
        )
        self.assertFalse(result["valid"])
    def test_unknown_top_level_field_fails_validation(self) -> None:
        report = self.valid_report()
        report["unexpected_field"] = "not allowed"
        self.write_report(report)
        result = validate_posture_report(
            self.report_path,
            SCHEMA_PATH,
        )
        self.assertFalse(result["valid"])
    def test_invalid_json_returns_error(self) -> None:
        self.report_path.write_text(
            "{broken json",
            encoding="utf-8",
        )
        result = validate_posture_report(
            self.report_path,
            SCHEMA_PATH,
        )
        self.assertFalse(result["valid"])
        self.assertEqual(result["status"], "ERROR")
    def test_missing_report_returns_error(self) -> None:
        result = validate_posture_report(
            self.report_path,
            SCHEMA_PATH,
        )
        self.assertFalse(result["valid"])
        self.assertEqual(result["status"], "ERROR")
    def test_missing_schema_returns_error(self) -> None:
        self.write_report(self.valid_report())
        missing_schema = Path(self.temp_dir.name) / "missing-schema.json"
        result = validate_posture_report(
            self.report_path,
            missing_schema,
        )
        self.assertFalse(result["valid"])
        self.assertEqual(result["status"], "ERROR")
if __name__ == "__main__":
    unittest.main(verbosity=2)