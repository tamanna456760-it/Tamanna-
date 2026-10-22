File: ids/tests/test_security_config.py

"""Configuration safety tests for Tamanna AI IDS."""
import json
import unittest
from pathlib import Path
IDS_DIR = Path(__file__).resolve().parents[1]
CONFIG_FILE = IDS_DIR / "ids_config.json"
class TestIDSSecurityConfig(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with CONFIG_FILE.open("r", encoding="utf-8") as file:
            cls.config = json.load(file)
    def test_configuration_is_valid_json_object(self):
        self.assertIsInstance(self.config, dict)
    def test_project_metadata(self):
        self.assertEqual(self.config.get("project"), "Tamanna AI")
        self.assertEqual(self.config.get("owner"), "HM INSAN ALI")
    def test_monitor_only_mode(self):
        self.assertEqual(self.config.get("mode"), "monitor_only")
    def test_automatic_ip_blocking_is_disabled(self):
        enforcement = self.config.get("enforcement", {})
        self.assertFalse(
            enforcement.get("automatic_ip_blocking", True)
        )
    def test_system_firewall_modification_is_disabled(self):
        enforcement = self.config.get("enforcement", {})
        self.assertFalse(
            enforcement.get("modify_system_firewall", True)
        )
    def test_manual_approval_is_required(self):
        enforcement = self.config.get("enforcement", {})
        self.assertTrue(enforcement.get("manual_approval", False))
    def test_event_storage_limits_are_positive(self):
        collection = self.config.get("collection", {})
        self.assertGreater(collection.get("max_event_size", 0), 0)
        self.assertGreater(collection.get("max_in_memory_events", 0), 0)
    def test_secret_redaction_is_enabled(self):
        collection = self.config.get("collection", {})
        self.assertTrue(collection.get("redact_secrets", False))
    def test_failed_login_threshold_is_positive(self):
        detection = self.config.get("detection", {})
        self.assertGreater(
            detection.get("failed_login_threshold", 0),
            0,
        )
        self.assertGreater(
            detection.get("failed_login_window_seconds", 0),
            0,
        )
    def test_request_rate_threshold_is_positive(self):
        detection = self.config.get("detection", {})
        self.assertGreater(
            detection.get("request_rate_threshold", 0),
            0,
        )
        self.assertGreater(
            detection.get("request_rate_window_seconds", 0),
            0,
        )
if __name__ == "__main__":
    unittest.main()