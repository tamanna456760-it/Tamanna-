"""Unit tests for Tamanna AI event log health checker.
Owner: HM INSAN ALI
"""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from endpoint_security.event_log_health import check_event_log
class TestEventLogHealth(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.log_path = Path(self.temp_dir.name) / "events.jsonl"
    def tearDown(self):
        self.temp_dir.cleanup()
    def test_missing_log_is_reported(self):
        result = check_event_log(self.log_path)
        self.assertEqual(result["status"], "MISSING")
    @patch("endpoint_security.event_log_health.validate_log")
    @patch("endpoint_security.event_log_health.validate_event_log")
    def test_valid_log_passes(self, mock_schema, mock_jsonl):
        self.log_path.write_text(
            json.dumps({
                "event_type": "health_check",
                "timestamp": "2026-10-13T00:00:00Z",
                "severity": "info",
            }) + "\n",
            encoding="utf-8",
        )
        mock_jsonl.return_value = {"valid": True}
        mock_schema.return_value = {"valid": True}
        result = check_event_log(self.log_path)
        self.assertEqual(result["status"], "PASS")
    @patch("endpoint_security.event_log_health.validate_log")
    @patch("endpoint_security.event_log_health.validate_event_log")
    def test_malformed_log_fails(self, mock_schema, mock_jsonl):
        self.log_path.write_text(
            '{"event_type":\n',
            encoding="utf-8",
        )
        mock_jsonl.return_value = {
            "valid": False,
            "errors": ["Invalid JSON on line 1"],
        }
        mock_schema.return_value = {
            "valid": False,
            "errors": ["Invalid event"],
        }
        result = check_event_log(self.log_path)
        self.assertEqual(result["status"], "FAIL")
    @patch("endpoint_security.event_log_health.validate_log")
    @patch("endpoint_security.event_log_health.validate_event_log")
    def test_schema_failure_fails(self, mock_schema, mock_jsonl):
        self.log_path.write_text('{"message": "missing fields"}\n', encoding="utf-8")
        mock_jsonl.return_value = {"valid": True}
        mock_schema.return_value = {
            "valid": False,
            "errors": ["Missing event_type or timestamp"],
        }
        result = check_event_log(self.log_path)
        self.assertEqual(result["status"], "FAIL")
    def test_directory_path_is_rejected(self):
        result = check_event_log(Path(self.temp_dir.name))
        self.assertEqual(result["status"], "ERROR")
if __name__ == "__main__":
    unittest.main(verbosity=2)