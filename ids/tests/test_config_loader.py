File: ids/tests/test_config_loader.py

"""Tests for the Tamanna AI IDS configuration loader."""
import json
import tempfile
import unittest
from pathlib import Path
from ids.config_loader import IDSConfigError, load_config
def valid_config():
    """Return a valid monitor-only test configuration."""
    return {
        "project": "Tamanna AI",
        "owner": "HM INSAN ALI",
        "version": "1.0.0",
        "enabled": True,
        "mode": "monitor_only",
        "detection": {
            "failed_login_threshold": 5,
            "failed_login_window": 300,
            "request_rate_threshold": 60,
            "request_rate_window": 60,
        },
        "collection": {
            "enabled": True,
            "max_event_size": 16384,
            "max_in_memory_events": 1000,
            "redact_secrets": True,
        },
        "alerts": {
            "enabled": True,
            "minimum_severity": "medium",
            "include_reason": True,
        },
        "storage": {
            "events_file": "data/security_events.jsonl",
            "report_file": "reports/ids_report.json",
        },
        "enforcement": {
            "automatic_ip_blocking": False,
            "modify_system_firewall": False,
            "manual_approval": True,
        },
    }
class TestIDSConfigLoader(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.config_path = Path(self.temp_dir.name) / "ids_config.json"
    def tearDown(self):
        self.temp_dir.cleanup()
    def write_config(self, config):
        self.config_path.write_text(
            json.dumps(config),
            encoding="utf-8",
        )
    def test_load_valid_configuration(self):
        self.write_config(valid_config())
        config = load_config(self.config_path)
        self.assertEqual(config["project"], "Tamanna AI")
        self.assertEqual(config["mode"], "monitor_only")
    def test_missing_file_is_rejected(self):
        with self.assertRaises(IDSConfigError):
            load_config(self.config_path)
    def test_invalid_json_is_rejected(self):
        self.config_path.write_text(
            "{invalid json",
            encoding="utf-8",
        )
        with self.assertRaises(IDSConfigError):
            load_config(self.config_path)
    def test_non_object_json_is_rejected(self):
        self.config_path.write_text(
            "[]",
            encoding="utf-8",
        )
        with self.assertRaises(IDSConfigError):
            load_config(self.config_path)
    def test_wrong_project_is_rejected(self):
        config = valid_config()
        config["project"] = "Other Project"
        self.write_config(config)
        with self.assertRaises(IDSConfigError):
            load_config(self.config_path)
    def test_unsupported_mode_is_rejected(self):
        config = valid_config()
        config["mode"] = "automatic_blocking"
        self.write_config(config)
        with self.assertRaises(IDSConfigError):
            load_config(self.config_path)
    def test_zero_threshold_is_rejected(self):
        config = valid_config()
        config["detection"]["failed_login_threshold"] = 0
        self.write_config(config)
        with self.assertRaises(IDSConfigError):
            load_config(self.config_path)
    def test_boolean_threshold_is_rejected(self):
        config = valid_config()
        config["detection"]["request_rate_threshold"] = True
        self.write_config(config)
        with self.assertRaises(IDSConfigError):
            load_config(self.config_path)
    def test_automatic_blocking_is_rejected(self):
        config = valid_config()
        config["enforcement"]["automatic_ip_blocking"] = True
        self.write_config(config)
        with self.assertRaises(IDSConfigError):
            load_config(self.config_path)
    def test_firewall_modification_is_rejected(self):
        config = valid_config()
        config["enforcement"]["modify_system_firewall"] = True
        self.write_config(config)
        with self.assertRaises(IDSConfigError):
            load_config(self.config_path)
    def test_missing_manual_approval_is_rejected(self):
        config = valid_config()
        config["enforcement"]["manual_approval"] = False
        self.write_config(config)
        with self.assertRaises(IDSConfigError):
            load_config(self.config_path)
    def test_secret_redaction_must_be_enabled(self):
        config = valid_config()
        config["collection"]["redact_secrets"] = False
        self.write_config(config)
        with self.assertRaises(IDSConfigError):
            load_config(self.config_path)
if __name__ == "__main__":
    unittest.main()