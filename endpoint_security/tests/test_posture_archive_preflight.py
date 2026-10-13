"""Tests for the read-only posture archive preflight checker.
Owner: HM INSAN ALI
"""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from endpoint_security.posture_archive_preflight import preflight_archive
PROJECT = "Tamanna AI"
OWNER = "HM INSAN ALI"
class TestPostureArchivePreflight(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.index_path = self.root / "archive-index.json"
        self.valid_index = {
            "project": PROJECT,
            "owner": OWNER,
            "reports": [
                {
                    "filename": "report.json",
                    "sha256": hashlib.sha256(b"example").hexdigest(),
                    "status": "STRUCTURE_READ",
                }
            ],
        }
        self.write_index(self.valid_index)
    def tearDown(self):
        self.temp_dir.cleanup()
    def write_index(self, value):
        self.index_path.write_text(
            json.dumps(value),
            encoding="utf-8",
        )
    def test_valid_index_passes(self):
        result = preflight_archive(self.index_path)
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["findings"], [])
        self.assertTrue(result["read_only"])
    def test_wrong_project_requires_review(self):
        index = dict(self.valid_index)
        index["project"] = "Other Project"
        self.write_index(index)
        result = preflight_archive(self.index_path)
        self.assertEqual(result["status"], "REVIEW_REQUIRED")
        self.assertIn("PROJECT_MISMATCH", result["findings"])
    def test_wrong_owner_requires_review(self):
        index = dict(self.valid_index)
        index["owner"] = "Unknown Owner"
        self.write_index(index)
        result = preflight_archive(self.index_path)
        self.assertIn("OWNER_MISMATCH", result["findings"])
    def test_duplicate_filename_is_detected(self):
        index = dict(self.valid_index)
        index["reports"] = [
            dict(self.valid_index["reports"][0]),
            dict(self.valid_index["reports"][0]),
        ]
        self.write_index(index)
        result = preflight_archive(self.index_path)
        self.assertIn(
            "REPORT_1_DUPLICATE_FILENAME",
            result["findings"],
        )
    def test_invalid_hash_is_detected(self):
        index = dict(self.valid_index)
        index["reports"] = [
            dict(self.valid_index["reports"][0], sha256="not-a-hash")
        ]
        self.write_index(index)
        result = preflight_archive(self.index_path)
        self.assertIn("REPORT_0_INVALID_SHA256", result["findings"])
    def test_path_traversal_is_detected(self):
        index = dict(self.valid_index)
        index["reports"] = [
            dict(self.valid_index["reports"][0], filename="../report.json")
        ]
        self.write_index(index)
        result = preflight_archive(self.index_path)
        self.assertIn("REPORT_0_UNSAFE_FILENAME", result["findings"])
    def test_unknown_status_is_detected(self):
        index = dict(self.valid_index)
        index["reports"] = [
            dict(self.valid_index["reports"][0], status="TRUSTED")
        ]
        self.write_index(index)
        result = preflight_archive(self.index_path)
        self.assertIn("REPORT_0_UNKNOWN_STATUS", result["findings"])
    def test_non_list_reports_is_detected(self):
        index = dict(self.valid_index)
        index["reports"] = {}
        self.write_index(index)
        result = preflight_archive(self.index_path)
        self.assertIn("REPORTS_MUST_BE_LIST", result["findings"])
    def test_missing_index_requires_review(self):
        result = preflight_archive(self.root / "missing.json")
        self.assertEqual(result["status"], "REVIEW_REQUIRED")
        self.assertIn("INDEX_NOT_FOUND", result["findings"])
    def test_invalid_json_requires_review(self):
        self.index_path.write_text("{invalid", encoding="utf-8")
        result = preflight_archive(self.index_path)
        self.assertEqual(result["status"], "REVIEW_REQUIRED")
        self.assertIn(
            "INDEX_UNREADABLE_OR_INVALID_JSON",
            result["findings"],
        )
if __name__ == "__main__":
    unittest.main()