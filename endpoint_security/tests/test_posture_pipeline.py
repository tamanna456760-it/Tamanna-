#!/usr/bin/env python3
"""Tests for the Tamanna AI posture report pipeline.
Owner: HM INSAN ALI
Uses temporary files only. Does not perform live security scans.
"""
from __future__ import annotations
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from endpoint_security.posture_pipeline import run_pipeline
class TestPosturePipeline(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.root = Path(self.temp_dir.name)
        self.input_path = self.root / "checks.json"
        self.output_path = self.root / "reports" / "posture.json"
        self.schema_path = self.root / "schema.json"
        self.input_path.write_text(
            json.dumps([
                {
                    "name": "configuration_policy",
                    "status": "PASS",
                    "details": "Example test result.",
                }
            ]),
            encoding="utf-8",
        )
        # The validator is mocked in these tests, so this schema is only
        # a placeholder file required by run_pipeline().
        self.schema_path.write_text("{}", encoding="utf-8")
    def test_pipeline_writes_report_and_validates_it(self) -> None:
        with patch(
            "endpoint_security.posture_pipeline.validate_posture_report",
            return_value={"status": "VALID"},
        ) as validator:
            result = run_pipeline(
                self.input_path,
                self.output_path,
                self.schema_path,
            )
        self.assertTrue(self.output_path.is_file())
        self.assertEqual(result["project"], "Tamanna AI")
        self.assertEqual(result["owner"], "HM INSAN ALI")
        self.assertEqual(result["schema_validation"], "VALID")
        self.assertTrue(result["read_only"])
        validator.assert_called_once_with(
            self.output_path,
            self.schema_path,
        )
        report = json.loads(self.output_path.read_text(encoding="utf-8"))
        self.assertEqual(report["checks"][0]["name"], "configuration_policy")
    def test_existing_output_is_not_overwritten(self) -> None:
        self.output_path.parent.mkdir(parents=True)
        self.output_path.write_text("KEEP THIS FILE", encoding="utf-8")
        with self.assertRaises(FileExistsError):
            run_pipeline(
                self.input_path,
                self.output_path,
                self.schema_path,
            )
        self.assertEqual(
            self.output_path.read_text(encoding="utf-8"),
            "KEEP THIS FILE",
        )
    def test_missing_input_is_rejected(self) -> None:
        with self.assertRaises(FileNotFoundError):
            run_pipeline(
                self.root / "missing.json",
                self.output_path,
                self.schema_path,
            )
    def test_missing_schema_is_rejected(self) -> None:
        with self.assertRaises(FileNotFoundError):
            run_pipeline(
                self.input_path,
                self.output_path,
                self.root / "missing-schema.json",
            )
    def test_invalid_input_json_is_rejected(self) -> None:
        self.input_path.write_text("{invalid", encoding="utf-8")
        with self.assertRaises(json.JSONDecodeError):
            run_pipeline(
                self.input_path,
                self.output_path,
                self.schema_path,
            )
if __name__ == "__main__":
    unittest.main(verbosity=2)