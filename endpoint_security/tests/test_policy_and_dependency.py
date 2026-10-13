"""Unit tests for Tamanna AI policy and dependency checkers.
Owner: HM INSAN ALI
"""
import json
import tempfile
import unittest
from pathlib import Path
from endpoint_security.policy_checker import check_policy
from endpoint_security.dependency_checker import check_requirements
class TestPolicyChecker(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.config_path = Path(self.temp_dir.name) / "endpoint_config.json"
        self.config = {
            "project": "Tamanna AI",
            "owner": "HM INSAN ALI",
            "enabled": True,
            "mode": "monitor_only",
            "monitoring": {},
            "process_monitoring": {
                "collect_command_line": False,
                "collect_environment_variables": False
            },
            "file_integrity": {"enabled": True},
            "logging": {
                "enabled": True,
                "redact_secrets": True
            },
            "enforcement": {
                "kill_processes": False,
                "quarantine_files": False,
                "delete_files": False,
                "modify_system_settings": False,
                "require_manual_approval": True
            }
        }
    def tearDown(self):
        self.temp_dir.cleanup()
    def write_config(self):
        self.config_path.write_text(
            json.dumps(self.config),
            encoding="utf-8"
        )
    def test_safe_monitor_only_policy_passes(self):
        self.write_config()
        result = check_policy(self.config_path)
        self.assertTrue(result["valid"], result)
    def test_enforcement_enabled_is_rejected(self):
        self.config["enforcement"]["kill_processes"] = True
        self.write_config()
        result = check_policy(self.config_path)
        self.assertFalse(result["valid"])
    def test_command_line_collection_is_rejected(self):
        self.config["process_monitoring"]["collect_command_line"] = True
        self.write_config()
        result = check_policy(self.config_path)
        self.assertFalse(result["valid"])
    def test_secret_redaction_must_be_enabled(self):
        self.config["logging"]["redact_secrets"] = False
        self.write_config()
        result = check_policy(self.config_path)
        self.assertFalse(result["valid"])
    def test_missing_config_is_rejected(self):
        result = check_policy(
            Path(self.temp_dir.name) / "missing.json"
        )
        self.assertFalse(result["valid"])
class TestDependencyChecker(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.requirements_path = Path(self.temp_dir.name) / "requirements.txt"
    def tearDown(self):
        self.temp_dir.cleanup()
    def test_exactly_pinned_requirement_is_accepted(self):
        self.requirements_path.write_text(
            "psutil==6.0.0\n",
            encoding="utf-8"
        )
        result = check_requirements(self.requirements_path)
        self.assertTrue(result["valid"], result)
    def test_unpinned_requirement_is_flagged(self):
        self.requirements_path.write_text(
            "psutil>=5.9\n",
            encoding="utf-8"
        )
        result = check_requirements(self.requirements_path)
        self.assertFalse(result["valid"])
    def test_empty_requirements_is_rejected(self):
        self.requirements_path.write_text("", encoding="utf-8")
        result = check_requirements(self.requirements_path)
        self.assertFalse(result["valid"])
    def test_missing_requirements_file_is_rejected(self):
        result = check_requirements(
            Path(self.temp_dir.name) / "missing.txt"
        )
        self.assertFalse(result["valid"])
if __name__ == "__main__":
    unittest.main(verbosity=2)