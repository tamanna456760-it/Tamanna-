"""Security-focused tests for the IDS configuration loader."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from ids.config_loader import load_config
class TestConfigLoaderSecurity(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.config_path = Path(self.temp_dir.name) / "ids_config.json"
        self.config = {
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
            "enforcement": {
                "automatic_ip_blocking": False,
                "modify_system_firewall": False,
                "manual_approval": True,
            },
        }
    def tearDown(self):
        self.temp_dir.cleanup()
    def write_config(self):
        self.config_path.write_text(
            json.dumps(self.config),
            encoding="utf-8",
        )
    def test_rejects_automatic_ip_blocking(self):
        self.config["enforcement"]["automatic_ip_blocking"] = True
        self.write_config()
        with patch("ids.config_loader.CONFIG_PATH", self.config_path):
            with self.assertRaises((ValueError, TypeError)):
                load_config()
    def test_rejects_firewall_modification(self):
        self.config["enforcement"]["modify_system_firewall"] = True
        self.write_config()
        with patch("ids.config_loader.CONFIG_PATH", self.config_path):
            with self.assertRaises((ValueError, TypeError)):
                load_config()
    def test_rejects_unsupported_mode(self):
        self.config["mode"] = "active"
        self.write_config()
        with patch("ids.config_loader.CONFIG_PATH", self.config_path):
            with self.assertRaises((ValueError, TypeError)):
                load_config()
    def test_rejects_secret_redaction_disabled(self):
        self.config["collection"]["redact_secrets"] = False
        self.write_config()
        with patch("ids.config_loader.CONFIG_PATH", self.config_path):
            with self.assertRaises((ValueError, TypeError)):
                load_config()
if __name__ == "__main__":
    unittest.main()