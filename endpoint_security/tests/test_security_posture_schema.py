#!/usr/bin/env python3
"""Tests for the Tamanna AI security posture JSON Schema.
Owner: HM INSAN ALI
These tests validate schema structure and basic required fields.
They do not perform full JSON Schema validation.
"""
from __future__ import annotations
import json
import unittest
from pathlib import Path
from typing import Any
SCHEMA_PATH = (
    Path(__file__).resolve().parents[1]
    / "security_posture_schema.json"
)
class TestSecurityPostureSchema(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        with SCHEMA_PATH.open("r", encoding="utf-8") as handle:
            cls.schema = json.load(handle)
    def test_schema_is_json_object(self) -> None:
        self.assertIsInstance(self.schema, dict)
    def test_schema_uses_supported_draft_identifier(self) -> None:
        self.assertEqual(
            self.schema.get("$schema"),
            "https://json-schema.org/draft/2020-12/schema",
        )
    def test_schema_requires_identity_and_check_counts(self) -> None:
        required = self.schema.get("required", [])
        for field in (
            "project",
            "owner",
            "generated_at_utc",
            "status",
            "checks",
            "checks_passed",
            "checks_failed",
            "checks_error",
            "read_only",
        ):
            with self.subTest(field=field):
                self.assertIn(field, required)
    def test_project_and_owner_are_fixed(self) -> None:
        properties = self.schema["properties"]
        self.assertEqual(
            properties["project"]["const"],
            "Tamanna AI",
        )
        self.assertEqual(
            properties["owner"]["const"],
            "HM INSAN ALI",
        )
    def test_read_only_must_be_true(self) -> None:
        self.assertIs(
            self.schema["properties"]["read_only"]["const"],
            True,
        )
    def test_check_statuses_are_defined(self) -> None:
        checks_schema = self.schema["properties"]["checks"]
        item_properties = checks_schema["items"]["properties"]
        statuses = item_properties["status"]["enum"]
        self.assertIn("PASS", statuses)
        self.assertIn("FAIL", statuses)
        self.assertIn("ERROR", statuses)
    def test_summary_counts_are_non_negative_integers(self) -> None:
        properties = self.schema["properties"]
        for field in (
            "checks_passed",
            "checks_failed",
            "checks_error",
        ):
            with self.subTest(field=field):
                self.assertEqual(
                    properties[field]["type"],
                    "integer",
                )
                self.assertEqual(
                    properties[field]["minimum"],
                    0,
                )
    def test_schema_disallows_unknown_top_level_fields(self) -> None:
        self.assertIs(
            self.schema.get("additionalProperties"),
            False,
        )
    def test_schema_file_is_present(self) -> None:
        self.assertTrue(SCHEMA_PATH.is_file())
    def test_example_identity_matches_schema(self) -> None:
        example: dict[str, Any] = {
            "project": "Tamanna AI",
            "owner": "HM INSAN ALI",
            "read_only": True,
        }
        properties = self.schema["properties"]
        for field in ("project", "owner", "read_only"):
            self.assertEqual(
                example[field],
                properties[field]["const"],
            )
if __name__ == "__main__":
    unittest.main(verbosity=2)