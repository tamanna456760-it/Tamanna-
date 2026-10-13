#!/usr/bin/env python3
"""Unit tests for the Tamanna AI configuration drift detector.
Owner: HM INSAN ALI
Tests are local and non-destructive.
"""
from __future__ import annotations
import json
import tempfile
import unittest
from pathlib import Path
from endpoint_security.config_drift_detector import detect_config_drift
SAFE_CONFIG = {
    "project": "Tamanna AI",
    "owner": "HM INSAN ALI",
    "enabled": True,
    "mode": "monitor_only",
    "process_monitoring": {
        "collect_command_line": False,
        "collect_environment_variables": False,
    },
    "logging": {
        "enabled": True,
        "redact_secrets": True,
    },
    "enforcement": {
        "kill_processes": False,
        "quarantine_files": False,
        "delete_files": False,
        "modify_system_settings": False,
        "require_manual_approval": True,
    },
}
class TestConfigDriftDetector(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.config_path = Path(self.temp_dir.name) / "endpoint_config.json"
    def write_config(self, config: object) -> None:
        self.config_path.write_text(
            json.dumps(config),
            encoding="utf-8",
        )
    def test_safe_configuration_has_no_drift(self) -> None:
        self.write_config(SAFE_CONFIG)
        result = detect_config_drift(self.config_path)
        self.assertTrue(result["valid"])
        self.assertEqual(result["status"], "NO_DRIFT")
        self.assertEqual(result["drift_count"], 0)
        self.assertTrue(result["read_only"])
    def test_changed_security_setting_is_detected(self) -> None:
        config = json.loads(json.dumps(SAFE_CONFIG))
        config["mode"] = "enforce"
        self.write_config(config)
        result = detect_config_drift(self.config_path)
        self.assertTrue(result["valid"])
        self.assertEqual(result["status"], "DRIFT_DETECTED")
        self.assertTrue(
            any(
                item["setting"] == "mode"
                and item["status"] == "CHANGED"
                for item in result["drift"]
            )
        )
    def test_missing_setting_is_detected(self) -> None:
        config = json.loads(json.dumps(SAFE_CONFIG))
        del config["logging"]["redact_secrets"]
        self.write_config(config)
        result = detect_config_drift(self.config_path)
        self.assertEqual(result["status"], "DRIFT_DETECTED")
        self.assertTrue(
            any(
                item["setting"] == "logging.redact_secrets"
                and item["status"] == "MISSING"
                for item in result["drift"]
            )
        )
    def test_enabled_destructive_action_is_detected(self) -> None:
        config = json.loads(json.dumps(SAFE_CONFIG))
        config["enforcement"]["delete_files"] = True
        self.write_config(config)
        result = detect_config_drift(self.config_path)
        self.assertEqual(result["status"], "DRIFT_DETECTED")
        self.assertTrue(
            any(
                item["setting"] == "enforcement.delete_files"
                and item["status"] == "CHANGED"
                for item in result["drift"]
            )
        )
    def test_boolean_integer_type_difference_is_detected(self) -> None:
        config = json.loads(json.dumps(SAFE_CONFIG))
        config["enabled"] = 1
        self.write_config(config)
        result = detect_config_drift(self.config_path)
        self.assertEqual(result["status"], "DRIFT_DETECTED")
    def test_invalid_json_returns_error(self) -> None:
        self.config_path.write_text("{invalid json", encoding="utf-8")
        result = detect_config_drift(self.config_path)
        self.assertFalse(result["valid"])
        self.assertEqual(result["status"], "ERROR")
        self.assertTrue(result["errors"])
    def test_missing_file_returns_error(self) -> None:
        result = detect_config_drift(self.config_path)
        self.assertFalse(result["valid"])
        self.assertEqual(result["status"], "ERROR")
    def test_non_object_json_returns_error(self) -> None:
        self.config_path.write_text("[]", encoding="utf-8")
        result = detect_config_drift(self.config_path)
        self.assertFalse(result["valid"])
        self.assertEqual(result["status"], "ERROR")
if __name__ == "__main__":
    unittest.main(verbosity=2)