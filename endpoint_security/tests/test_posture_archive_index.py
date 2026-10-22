#!/usr/bin/env python3
"""Tests for the read-only Tamanna AI posture archive index.
Owner: HM INSAN ALI
"""
from __future__ import annotations
import json
import tempfile
import unittest
from pathlib import Path
from endpoint_security.posture_archive_index import index_reports, sha256_file
class TestPostureArchiveIndex(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.root = Path(self.temp_dir.name)
        self.report_dir = self.root / "reports"
        self.report_dir.mkdir()
    def write_json(self, name: str, value: object) -> Path:
        path = self.report_dir / name
        path.write_text(json.dumps(value), encoding="utf-8")
        return path
    def test_missing_directory_is_reported(self) -> None:
        result = index_reports(self.root / "missing")
        self.assertEqual(result["status"], "REPORT_DIRECTORY_MISSING")
        self.assertEqual(result["reports_found"], 0)
        self.assertTrue(result["read_only"])
    def test_empty_directory_has_no_reports(self) -> None:
        result = index_reports(self.report_dir)
        self.assertEqual(result["status"], "NO_REPORTS")
        self.assertEqual(result["reports_found"], 0)
    def test_matching_report_is_indexed(self) -> None:
        path = self.write_json("valid.json", {
            "project": "Tamanna AI",
            "owner": "HM INSAN ALI",
            "status": "VALID",
        })
        result = index_reports(self.report_dir)
        self.assertEqual(result["status"], "REPORTS_INDEXED")
        self.assertEqual(result["reports_found"], 1)
        entry = result["reports"][0]
        self.assertEqual(entry["file"], "valid.json")
        self.assertEqual(entry["status"], "STRUCTURE_READ")
        self.assertEqual(entry["report_status"], "VALID")
        self.assertEqual(entry["sha256"], sha256_file(path))
    def test_identity_mismatch_is_flagged(self) -> None:
        self.write_json("other.json", {
            "project": "Other Project",
            "owner": "Someone Else",
            "status": "VALID",
        })
        result = index_reports(self.report_dir)
        self.assertEqual(result["reports"][0]["status"], "IDENTITY_MISMATCH")
    def test_invalid_json_is_marked_unreadable(self) -> None:
        (self.report_dir / "broken.json").write_text(
            "{invalid",
            encoding="utf-8",
        )
        result = index_reports(self.report_dir)
        self.assertEqual(result["reports_unreadable"], 1)
        self.assertEqual(result["reports"][0]["status"], "UNREADABLE")
    def test_json_array_is_rejected_as_report_structure(self) -> None:
        self.write_json("array.json", ["not", "a", "report"])
        result = index_reports(self.report_dir)
        self.assertEqual(
            result["reports"][0]["status"],
            "INVALID_JSON_STRUCTURE",
        )
    def test_non_json_files_are_ignored(self) -> None:
        (self.report_dir / "notes.txt").write_text("hello", encoding="utf-8")
        result = index_reports(self.report_dir)
        self.assertEqual(result["reports_found"], 0)
        self.assertEqual(result["status"], "NO_REPORTS")
if __name__ == "__main__":
    unittest.main(verbosity=2)