#!/usr/bin/env python3
"""Unit tests for Tamanna AI posture archive integrity verification.
Owner: HM INSAN ALI
Uses temporary test files only. Does not modify real security reports.
"""
from __future__ import annotations
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from endpoint_security.posture_archive_verifier import verify_archive
class TestPostureArchiveVerifier(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.root = Path(self.temp_dir.name)
        self.report_dir = self.root / "reports"
        self.report_dir.mkdir()
        self.report_path = self.report_dir / "report.json"
        self.report_path.write_text(
            json.dumps({
                "project": "Tamanna AI",
                "owner": "HM INSAN ALI",
                "status": "VALID",
            }),
            encoding="utf-8",
        )
        self.index_path = self.root / "index.json"
        self.write_index()
    def write_index(self, filename: str = "report.json") -> None:
        raw = (self.report_dir / filename).read_bytes()
        report_hash = hashlib.sha256(raw).hexdigest()
        index = {
            "project": "Tamanna AI",
            "owner": "HM INSAN ALI",
            "reports": [{
                "file": filename,
                "sha256": report_hash,
            }],
        }
        self.index_path.write_text(
            json.dumps(index),
            encoding="utf-8",
        )
    def test_matching_hash_passes(self) -> None:
        result = verify_archive(self.index_path, self.report_dir)
        self.assertEqual(result["status"], "MATCH")
        self.assertEqual(result["reports_matching"], 1)
        self.assertEqual(result["reports_with_issues"], 0)
        self.assertEqual(result["results"][0]["status"], "MATCH")
    def test_modified_report_is_detected(self) -> None:
        self.report_path.write_text(
            '{"project":"Tamanna AI","owner":"HM INSAN ALI","status":"CHANGED"}',
            encoding="utf-8",
        )
        result = verify_archive(self.index_path, self.report_dir)
        self.assertEqual(result["status"], "REVIEW_REQUIRED")
        self.assertEqual(
            result["results"][0]["status"],
            "HASH_MISMATCH",
        )
    def test_missing_report_is_detected(self) -> None:
        self.report_path.unlink()
        result = verify_archive(self.index_path, self.report_dir)
        self.assertEqual(result["status"], "REVIEW_REQUIRED")
        self.assertEqual(
            result["results"][0]["status"],
            "MISSING_OR_UNSAFE_FILE",
        )
    def test_invalid_hash_is_rejected(self) -> None:
        index = json.loads(self.index_path.read_text(encoding="utf-8"))
        index["reports"][0]["sha256"] = "not-a-sha256"
        self.index_path.write_text(json.dumps(index), encoding="utf-8")
        result = verify_archive(self.index_path, self.report_dir)
        self.assertEqual(result["status"], "REVIEW_REQUIRED")
        self.assertEqual(
            result["results"][0]["status"],
            "NO_VALID_BASELINE_HASH",
        )
    def test_invalid_project_is_rejected(self) -> None:
        index = json.loads(self.index_path.read_text(encoding="utf-8"))
        index["project"] = "Wrong Project"
        self.index_path.write_text(json.dumps(index), encoding="utf-8")
        with self.assertRaises(ValueError):
            verify_archive(self.index_path, self.report_dir)
    def test_missing_index_is_rejected(self) -> None:
        with self.assertRaises(FileNotFoundError):
            verify_archive(self.root / "missing.json", self.report_dir)
    def test_path_traversal_filename_is_rejected(self) -> None:
        index = json.loads(self.index_path.read_text(encoding="utf-8"))
        index["reports"][0]["file"] = "../outside.json"
        self.index_path.write_text(json.dumps(index), encoding="utf-8")
        result = verify_archive(self.index_path, self.report_dir)
        self.assertEqual(result["status"], "REVIEW_REQUIRED")
        self.assertEqual(
            result["results"][0]["status"],
            "INVALID_FILENAME",
        )
if __name__ == "__main__":
    unittest.main(verbosity=2)