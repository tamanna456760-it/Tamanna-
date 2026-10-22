#!/usr/bin/env python3
"""Tests for the Tamanna AI unified posture report builder.
Owner: HM INSAN ALI
Tests use temporary files and do not modify existing reports.
"""
from __future__ import annotations
import json
import tempfile
import unittest
from pathlib import Path
from endpoint_security.unified_posture_report import (
    build_posture_report,
    load_checks,
)
class TestUnifiedPostureReport(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.temp_path = Path(self.temp_dir.name)
    def test_all_passed_checks_produce_valid_report(self) -> None:
        report = build_posture_report([
            {"name": "config", "status": "PASS"},
            {"name": "logging", "status": "OK"},
        ])
        self.assertEqual(report["project"], "Tamanna AI")
        self.assertEqual(report["owner"], "HM INSAN ALI")
        self.assertEqual(report["status"], "VALID")
        self.assertEqual(report["checks_passed"], 2)
        self.assertEqual(report["checks_failed"], 0)
        self.assertEqual(report["checks_error"], 0)
        self.assertTrue(report["read_only"])
    def test_failed_check_requires_review(self) -> None:
        report = build_posture_report([
            {"name": "policy", "status": "FAIL"},
        ])
        self.assertEqual(report["status"], "REVIEW_REQUIRED")
        self.assertEqual(report["checks_failed"], 1)
    def test_unknown_status_counts_as_error(self) -> None:
        report = build_posture_report([
            {"name": "dependency", "status": "UNKNOWN"},
        ])
        self.assertEqual(report["status"], "REVIEW_REQUIRED")
        self.assertEqual(report["checks_error"], 1)
    def test_non_object_check_is_converted_to_error(self) -> None:
        report = build_posture_report([
            None,  # type: ignore[list-item]
        ])
        self.assertEqual(report["checks_error"], 1)
        self.assertEqual(report["checks"][0]["status"], "ERROR")
    def test_missing_check_name_gets_default_name(self) -> None:
        report = build_posture_report([
            {"status": "PASS"},
        ])
        self.assertEqual(report["checks"][0]["name"], "check_1")
    def test_empty_checks_produce_valid_report(self) -> None:
        report = build_posture_report([])
        self.assertEqual(report["status"], "VALID")
        self.assertEqual(report["checks"], [])
        self.assertEqual(report["checks_passed"], 0)
    def test_load_checks_accepts_json_array(self) -> None:
        input_path = self.temp_path / "checks.json"
        input_path.write_text(
            json.dumps([{"name": "config", "status": "PASS"}]),
            encoding="utf-8",
        )
        checks = load_checks(input_path)
        self.assertEqual(len(checks), 1)
        self.assertEqual(checks[0]["name"], "config")
    def test_load_checks_rejects_non_array(self) -> None:
        input_path = self.temp_path / "checks.json"
        input_path.write_text('{"name": "config"}', encoding="utf-8")
        with self.assertRaises(ValueError):
            load_checks(input_path)
    def test_load_checks_rejects_non_object_items(self) -> None:
        input_path = self.temp_path / "checks.json"
        input_path.write_text('[{"name":"config"}, 7]', encoding="utf-8")
        with self.assertRaises(ValueError):
            load_checks(input_path)
    def test_load_checks_rejects_invalid_json(self) -> None:
        input_path = self.temp_path / "checks.json"
        input_path.write_text("{invalid", encoding="utf-8")
        with self.assertRaises(json.JSONDecodeError):
            load_checks(input_path)
if __name__ == "__main__":
    unittest.main(verbosity=2)