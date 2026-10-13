"""Tests for Tamanna AI WAF event logger."""
import json
import os
import tempfile
import unittest
from waf.event_logger import WAFEventLogger
class TestWAFEventLogger(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.log_path = os.path.join(
            self.temp_dir.name, "waf_events.jsonl"
        )
        self.config = {
            "project": "Tamanna AI",
            "logging": {
                "enabled": True,
                "file": self.log_path,
                "redact_secrets": True,
                "max_event_size_bytes": 4096,
            },
        }
        self.logger = WAFEventLogger(self.config)
    def tearDown(self):
        self.temp_dir.cleanup()
    def test_event_is_written_as_json(self):
        result = self.logger.log_event({
            "status": "alert",
            "rule": "sql_injection",
        })
        self.assertTrue(result["logged"])
        self.assertTrue(os.path.isfile(self.log_path))
        with open(self.log_path, encoding="utf-8") as handle:
            record = json.loads(handle.readline())
        self.assertEqual(record["project"], "Tamanna AI")
        self.assertEqual(record["event"]["rule"], "sql_injection")
    def test_sensitive_fields_are_redacted(self):
        self.logger.log_event({
            "authorization": "Bearer secret-value",
            "password": "my-password",
            "details": {
                "api_key": "private-key",
            },
        })
        with open(self.log_path, encoding="utf-8") as handle:
            record = json.loads(handle.readline())
        event = record["event"]
        self.assertEqual(event["authorization"], "[REDACTED]")
        self.assertEqual(event["password"], "[REDACTED]")
        self.assertEqual(event["details"]["api_key"], "[REDACTED]")
    def test_oversized_event_is_rejected(self):
        config = {
            "logging": {
                "enabled": True,
                "file": self.log_path,
                "redact_secrets": True,
                "max_event_size_bytes": 100,
            }
        }
        logger = WAFEventLogger(config)
        result = logger.log_event({"message": "x" * 500})
        self.assertFalse(result["logged"])
        self.assertEqual(result["reason"], "event_too_large")
        self.assertFalse(os.path.exists(self.log_path))
    def test_disabled_logging_does_not_write_file(self):
        config = {
            "logging": {
                "enabled": False,
                "file": self.log_path,
            }
        }
        logger = WAFEventLogger(config)
        result = logger.log_event({"status": "alert"})
        self.assertFalse(result["logged"])
        self.assertEqual(result["reason"], "logging_disabled")
        self.assertFalse(os.path.exists(self.log_path))
    def test_non_json_serializable_event_is_rejected(self):
        result = self.logger.log_event({
            "unsafe_value": object(),
        })
        self.assertFalse(result["logged"])
        self.assertEqual(
            result["reason"],
            "event_not_json_serializable",
        )
if __name__ == "__main__":
    unittest.main()