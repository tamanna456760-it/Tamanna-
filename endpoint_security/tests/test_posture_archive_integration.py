"""Integration tests for Tamanna AI posture archive security.
Owner: HM INSAN ALI
These tests use temporary directories and do not modify real archive reports.
"""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from endpoint_security.posture_archive_index import index_reports
from endpoint_security.posture_archive_verifier import verify_archive
from endpoint_security.posture_archive_policy import check_archive_index
PROJECT = "Tamanna AI"
OWNER = "HM INSAN ALI"
class TestPostureArchiveIntegration(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.archive_dir = Path(self.temp_dir.name)
        self.report_path = self.archive_dir / "sample-report.json"
        self.report = {
            "project": PROJECT,
            "owner": OWNER,
            "status": "VALID",
            "read_only": True,
        }
        self.report_path.write_text(
            json.dumps(self.report, sort_keys=True),
            encoding="utf-8",
        )
    def tearDown(self):
        self.temp_dir.cleanup()
    def create_index(self):
        digest = hashlib.sha256(
            self.report_path.read_bytes()
        ).hexdigest()
        index = {
            "project": PROJECT,
            "owner": OWNER,
            "reports": [
                {
                    "filename": self.report_path.name,
                    "sha256": digest,
                    "status": "STRUCTURE_READ",
                }
            ],
        }
        index_path = self.archive_dir / "test-index.json"
        index_path.write_text(
            json.dumps(index),
            encoding="utf-8",
        )
        return index_path
    def test_report_hash_matches_index(self):
        index_path = self.create_index()
        result = verify_archive(
            index_path=index_path,
            report_dir=self.archive_dir,
        )
        self.assertIsInstance(result, dict)
        self.assertIn(
            result.get("status"),
            {"MATCH", "VALID", "PASS"},
        )
    def test_policy_accepts_valid_index(self):
        index_path = self.create_index()
        result = check_archive_index(index_path)
        self.assertIsInstance(result, dict)
        self.assertIn(
            result.get("status"),
            {"PASS", "VALID"},
        )
    def test_modified_report_is_detected(self):
        index_path = self.create_index()
        self.report["status"] = "CHANGED"
        self.report_path.write_text(
            json.dumps(self.report, sort_keys=True),
            encoding="utf-8",
        )
        result = verify_archive(
            index_path=index_path,
            report_dir=self.archive_dir,
        )
        self.assertIsInstance(result, dict)
        self.assertNotIn(
            result.get("status"),
            {"MATCH", "VALID", "PASS"},
        )
if __name__ == "__main__":
    unittest.main()