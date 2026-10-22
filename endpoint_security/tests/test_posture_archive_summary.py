"""Tests for Tamanna AI posture archive summary.
Owner: HM INSAN ALI
"""
import json
import tempfile
import unittest
from pathlib import Path
from endpoint_security.posture_archive_summary import build_summary
PROJECT = "Tamanna AI"
OWNER = "HM INSAN ALI"
class TestPostureArchiveSummary(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.result_path = self.root / "validator-result.json"
    def tearDown(self):
        self.temp_dir.cleanup()
    def write_result(self, result):
        self.result_path.write_text(
            json.dumps(result),
            encoding="utf-8",
        )
    def test_valid_result_produces_pass_summary(self):
        self.write_result({
            "project": PROJECT,
            "owner": OWNER,
            "status": "PASS",
            "validation": "VALID",
            "findings": [],
            "read_only": True,
        })
        summary = build_summary(self.result_path)
        self.assertEqual(summary["status"], "PASS")
        self.assertEqual(summary["project"], PROJECT)
        self.assertTrue(summary["read_only"])
        self.assertEqual(summary["findings"], [])
    def test_wrong_owner_requires_review(self):
        self.write_result({
            "project": PROJECT,
            "owner": "Unknown Owner",
            "status": "PASS",
            "validation": "VALID",
            "findings": [],
        })
        summary = build_summary(self.result_path)
        self.assertEqual(summary["status"], "REVIEW_REQUIRED")
        self.assertIn(
            "PROJECT_OR_OWNER_MISMATCH",
            summary["findings"],
        )
    def test_invalid_validation_requires_review(self):
        self.write_result({
            "project": PROJECT,
            "owner": OWNER,
            "status": "PASS",
            "validation": "INVALID",
            "findings": ["SCHEMA_ERROR"],
        })
        summary = build_summary(self.result_path)
        self.assertEqual(summary["status"], "REVIEW_REQUIRED")
        self.assertIn("SCHEMA_ERROR", summary["findings"])
    def test_non_object_json_requires_review(self):
        self.result_path.write_text("[]", encoding="utf-8")
        summary = build_summary(self.result_path)
        self.assertEqual(summary["status"], "REVIEW_REQUIRED")
        self.assertIn("RESULT_ROOT_NOT_OBJECT", summary["findings"])
    def test_invalid_json_requires_review(self):
        self.result_path.write_text("{invalid", encoding="utf-8")
        summary = build_summary(self.result_path)
        self.assertEqual(summary["status"], "REVIEW_REQUIRED")
        self.assertIn("RESULT_FILE_INVALID", summary["findings"])
    def test_missing_file_requires_review(self):
        summary = build_summary(self.root / "missing.json")
        self.assertEqual(summary["status"], "REVIEW_REQUIRED")
        self.assertIn(
            "RESULT_FILE_NOT_FOUND_OR_UNSAFE",
            summary["findings"],
        )
    def test_non_string_findings_require_review(self):
        self.write_result({
            "project": PROJECT,
            "owner": OWNER,
            "status": "PASS",
            "validation": "VALID",
            "findings": [123],
        })
        summary = build_summary(self.result_path)
        self.assertEqual(summary["status"], "REVIEW_REQUIRED")
        self.assertIn("RESULT_FINDINGS_INVALID", summary["findings"])
if __name__ == "__main__":
    unittest.main()