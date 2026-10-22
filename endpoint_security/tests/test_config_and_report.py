#!/usr/bin/env python3
"""Tests for Tamanna AI Endpoint Security configuration and reports.
Owner: HM INSAN ALI
"""
import json
import tempfile
import unittest
from pathlib import Path
from endpoint_security.config_validator import validate_config
from endpoint_security.report_generator import build_report
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG = PROJECT_ROOT / "endpoint_security" / "endpoint_config.json"
def load_default_config():
    with DEFAULT_CONFIG.open("r", encoding="utf-8") as file:
        return json.load(file)
class ConfigValidatorTests(unittest.TestCase):
    def test_default_config_is_valid(self):
        config = load_default_config()
        self.assertEqual(validate_config(config), [])
    def test_rejects_wrong_mode(self):
        config = load_default_config()
        config["mode"] = "enforce"
        errors = validate_config(config)
        self.assertTrue(any("mode" in error for error in errors))
    def test_rejects_process_termination(self):
        config = load_default_config()
        config["enforcement"]["kill_processes"] = True
        errors = validate_config(config)
        self.assertTrue(
            any("kill_processes" in error for error in errors)
        )
    def test_rejects_invalid_file_size(self):
        config = load_default_config()
        config["file_integrity"]["max_file_size_bytes"] = -1
        errors = validate_config(config)
        self.assertTrue(
            any("max_file_size_bytes" in error for error in errors)
        )
    def test_rejects_non_object_config(self):
        self.assertTrue(validate_config([]))
class ReportGeneratorTests(unittest.TestCase):
    def test_valid_config_report(self):
        report = build_report(DEFAULT_CONFIG)
        self.assertTrue(report["configuration_valid"])
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(report["mode"], "monitor_only")
    def test_missing_config_report_fails(self):
        missing_path = Path("/nonexistent/tamanna-config.json")
        report = build_report(missing_path)
        self.assertFalse(report["configuration_valid"])
        self.assertTrue(report["errors"])
    def test_invalid_json_report_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            config_path = Path(directory) / "invalid.json"
            config_path.write_text("{invalid json", encoding="utf-8")
            report = build_report(config_path)
            self.assertFalse(report["configuration_valid"])
            self.assertTrue(report["errors"])
    def test_report_does_not_enable_destructive_actions(self):
        report = build_report(DEFAULT_CONFIG)
        self.assertFalse(report["destructive_actions_enabled"])
if __name__ == "__main__":
    unittest.main(verbosity=2)