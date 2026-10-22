#!/usr/bin/env python3
"""Unit tests for Tamanna AI posture archive policy checks.
Owner: HM INSAN ALI
"""
from __future__ import annotations
import json
import tempfile
import unittest
from pathlib import Path
from endpoint_security.posture_archive_policy import check_archive_index
class TestPostureArchivePolicy(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.root = Path(self.temp_dir.name)
        self.index_path = self.root / "index.json"
    def write_index(self, data: object) -> None:
        self.index_path.write_text(
            json.dumps(data),
            encoding="utf-8",
        )
    @staticmethod
    def valid_entry(filename: str = "report.json") -> dict:
        return {
            "file": filename,
            "sha256": "a" * 64,
            "status": "STRUCTURE_READ",
        }
    def test_valid_index_passes(self) -> None:
        self.write_index({
            "project": "Tamanna AI",
            "owner": "HM INSAN ALI",
            "reports": [self.valid_entry()],
        })
        result = check_archive_index(self.index_path)
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["findings_count"], 0)
        self.assertTrue(result["read_only"])
    def test_wrong_project_is_flagged(self) -> None:
        self.write_index({
            "project": "Other Project",
            "owner": "HM INSAN ALI",
            "reports": [self.valid_entry()],
        })
        result = check_archive_index(self.index_path)
        self.assertEqual(result["status"], "REVIEW_REQUIRED")
        self.assertIn(
            "PROJECT_MISMATCH",
            [item["code"] for item in result["findings"]],
        )
    def test_wrong_owner_is_flagged(self) -> None:
        self.write_index({
            "project": "Tamanna AI",
            "owner": "Someone Else",
            "reports": [self.valid_entry()],
        })
        result = check_archive_index(self.index_path)
        self.assertIn(
            "OWNER_MISMATCH",
            [item["code"] for item in result["findings"]],
        )
    def test_duplicate_filename_is_flagged(self) -> None:
        self.write_index({
            "project": "Tamanna AI",
            "owner": "HM INSAN ALI",
            "reports": [
                self.valid_entry("report.json"),
                self.valid_entry("report.json"),
            ],
        })
        result = check_archive_index(self.index_path)
        self.assertIn(
            "DUPLICATE_FILENAME",
            [item["code"] for item in result["findings"]],
        )
    def test_invalid_hash_is_flagged(self) -> None:
        entry = self.valid_entry()
        entry["sha256"] = "not-a-hash"
        self.write_index({
            "project": "Tamanna AI",
            "owner": "HM INSAN ALI",
            "reports": [entry],
        })
        result = check_archive_index(self.index_path)
        self.assertIn(
            "INVALID_SHA256",
            [item["code"] for item in result["findings"]],
        )
    def test_path_traversal_filename_is_flagged(self) -> None:
        self.write_index({
            "project": "Tamanna AI",
            "owner": "HM INSAN ALI",
            "reports": [self.valid_entry("../outside.json")],
        })
        result = check_archive_index(self.index_path)
        self.assertIn(
            "INVALID_FILENAME",
            [item["code"] for item in result["findings"]],
        )
    def test_unknown_status_is_flagged(self) -> None:
        entry = self.valid_entry()
        entry["status"] = "TRUSTED"
        self.write_index({
            "project": "Tamanna AI",
            "owner": "HM INSAN ALI",
            "reports": [entry],
        })
        result = check_archive_index(self.index_path)
        self.assertIn(
            "UNKNOWN_ENTRY_STATUS",
            [item["code"] for item in result["findings"]],
        )
    def test_non_object_entry_is_flagged(self) -> None:
        self.write_index({
            "project": "Tamanna AI",
            "owner": "HM INSAN ALI",
            "reports": ["invalid-entry"],
        })
        result = check_archive_index(self.index_path)
        self.assertIn(
            "INVALID_ENTRY",
            [item["code"] for item in result["findings"]],
        )
    def test_non_list_reports_is_flagged(self) -> None:
        self.write_index({
            "project": "Tamanna AI",
            "owner": "HM INSAN ALI",
            "reports": {},
        })
        result = check_archive_index(self.index_path)
        self.assertIn(
            "REPORTS_NOT_LIST",
            [item["code"] for item in result["findings"]],
        )
    def test_missing_index_is_rejected(self) -> None:
        with self.assertRaises(FileNotFoundError):
            check_archive_index(self.root / "missing.json")
    def test_invalid_json_is_rejected(self) -> None:
        self.index_path.write_text("{invalid", encoding="utf-8")
        with self.assertRaises(json.JSONDecodeError):
            check_archive_index(self.index_path)
if __name__ == "__main__":
    unittest.main(verbosity=2)