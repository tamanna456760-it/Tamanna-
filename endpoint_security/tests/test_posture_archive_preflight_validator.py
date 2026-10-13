"""Tests for the read-only posture archive preflight schema validator.
Owner: HM INSAN ALI
"""
import json
import tempfile
import unittest
from pathlib import Path
from endpoint_security.posture_archive_preflight_validator import (
    DEFAULT_SCHEMA,
    validate_result,
)
PROJECT = "Tamanna AI"
OWNER = "HM INSAN ALI"
class TestPostureArchivePreflightValidator(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.result_path = self.root / "preflight-result.json"
        self.valid_result = {
            "project": PROJECT,
            "owner": OWNER,
            "status": "PASS",
            "findings": [],
            "report_count": 1,
            "read_only": True,
        }
    def tearDown(self):
        self.temp_dir.cleanup()
    def write_result(self, result):
        self.result_path.write_text(
            json.dumps(result),
            encoding="utf-8",
        )
    def test_valid_result_passes_schema(self):
        self.write_result(self.valid_result)
        result = validate_result(self.result_path, DEFAULT_SCHEMA)
        self.assertEqual(result["validation"], "VALID")
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["findings"], [])
    def test_wrong_owner_fails_schema(self):
        result_data = dict(self.valid_result)
        result_data["owner"] = "Wrong Owner"
        self.write_result(result_data)
        result = validate_result(self.result_path, DEFAULT_SCHEMA)
        self.assertEqual(result["validation"], "INVALID")
        self.assertEqual(result["status"], "REVIEW_REQUIRED")
    def test_pass_with_findings_fails_schema(self):
        result_data = dict(self.valid_result)
        result_data["findings"] = ["UNEXPECTED_FINDING"]
        self.write_result(result_data)
        result = validate_result(self.result_path, DEFAULT_SCHEMA)
        self.assertEqual(result["validation"], "INVALID")
    def test_review_required_without_findings_fails_schema(self):
        result_data = dict(self.valid_result)
        result_data["status"] = "REVIEW_REQUIRED"
        self.write_result(result_data)
        result = validate_result(self.result_path, DEFAULT_SCHEMA)
        self.assertEqual(result["validation"], "INVALID")
    def test_missing_result_file_returns_error(self):
        result = validate_result(
            self.root / "missing.json",
            DEFAULT_SCHEMA,
        )
        self.assertEqual(result["validation"], "ERROR")
        self.assertIn(
            "RESULT_FILE_UNREADABLE_OR_INVALID_JSON",
            result["findings"],
        )
    def test_invalid_json_returns_error(self):
        self.result_path.write_text("{invalid", encoding="utf-8")
        result = validate_result(self.result_path, DEFAULT_SCHEMA)
        self.assertEqual(result["validation"], "ERROR")
    def test_missing_schema_returns_error(self):
        self.write_result(self.valid_result)
        result = validate_result(
            self.result_path,
            self.root / "missing-schema.json",
        )
        self.assertEqual(result["validation"], "ERROR")
        self.assertIn(
            "SCHEMA_UNREADABLE_OR_INVALID_JSON",
            result["findings"],
        )
if __name__ == "__main__":
    unittest.main()