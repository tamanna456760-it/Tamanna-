#!/usr/bin/env python3
"""Integration tests for Tamanna AI endpoint security posture reports.
Owner: HM INSAN ALI
Tests report generation and JSON Schema validation together.
These tests do not run security scans or enforcement actions.
"""
from __future__ import annotations
import json
import tempfile
import unittest
from pathlib import Path
from endpoint_security.unified_posture_report import build_posture_report
from endpoint_security.posture_schema_validator import validate_posture_report
class TestPostureIntegration(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.temp_path = Path(self.temp_dir.name)
        self.schema_path = (
            Path(__file__).resolve().parents[1]
            / "security_posture_schema.json"
        )
    def write_report(self, checks: list[dict]) -> Path:
        report = build_posture_report(checks)
        report_path = self.temp_path / "posture_report.json"
        report_path.write_text(
            json.dumps(report, indent=2),
            encoding="utf-8",
        )
        return report_path
    def test_passing_report_has_valid_schema(self) -> None:
        report_path = self.write_report([
            {
                "name": "configuration_policy",
                "status": "PASS",
                "details": "Security policy checks passed.",
            }
        ])
        result = validate_posture_report(
            report_path,
            self.schema_path,
        )
        self.assertEqual(result.get("status"), "VALID")
    def test_failed_check_requires_review_but_schema_is_valid(self) -> None:
        report_path = self.write_report([
            {
                "name": "configuration_policy",
                "status": "FAIL",
                "details": "A security setting needs review.",
            }
        ])
        report = json.loads(report_path.read_text(encoding="utf-8"))
        self.assertEqual(report["status"], "REVIEW_REQUIRED")
        self.assertEqual(report["counts"]["checks_failed"], 1)
        result = validate_posture_report(
            report_path,
            self.schema_path,
        )
        self.assertEqual(result.get("status"), "VALID")
    def test_error_check_is_counted_and_schema_valid(self) -> None:
        report_path = self.write_report([
            {
                "name": "event_log_check",
                "status": "ERROR",
                "details": "The check could not complete.",
            }
        ])
        report = json.loads(report_path.read_text(encoding="utf-8"))
        self.assertEqual(report["counts"]["checks_error"], 1)
        self.assertEqual(report["status"], "REVIEW_REQUIRED")
        result = validate_posture_report(
            report_path,
            self.schema_path,
        )
        self.assertEqual(result.get("status"), "VALID")
    def test_empty_checks_produce_valid_report(self) -> None:
        report_path = self.write_report([])
        report = json.loads(report_path.read_text(encoding="utf-8"))
        self.assertEqual(report["status"], "VALID")
        self.assertEqual(report["counts"]["checks_passed"], 0)
        result = validate_posture_report(
            report_path,
            self.schema_path,
        )
        self.assertEqual(result.get("status"), "VALID")
if __name__ == "__main__":
    unittest.main(verbosity=2)