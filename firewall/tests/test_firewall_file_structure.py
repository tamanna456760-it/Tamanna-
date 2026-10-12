"""
Tamanna AI Firewall - File Structure Tests
Owner: HM INSAN ALI
"""
import json
import unittest
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parents[2]
FIREWALL_DIR = PROJECT_ROOT / "firewall"
REQUIRED_FILES = (
    "__init__.py",
    "firewall_config.json",
    "firewall_manager.py",
    "port_checker.py",
    "access_control.py",
    "audit_log.py",
    "rate_limiter.py",
    "threat_detector.py",
    "security_monitor.py",
    "api_protection.py",
    "policy_validator.py",
    "defense_score.py",
    "run_tests.py",
)
REQUIRED_TEST_FILES = (
    "test_firewall.py",
    "test_api_protection.py",
    "test_policy_validator.py",
    "test_defense_score.py",
    "test_access_control.py",
    "test_audit_log.py",
    "test_rate_limiter.py",
    "test_security_monitor.py",
    "test_threat_detector.py",
    "test_firewall_manager.py",
    "test_port_checker.py",
    "test_config.py",
    "test_imports.py",
)
class TestFirewallFileStructure(unittest.TestCase):
    def test_firewall_directory_exists(self):
        self.assertTrue(
            FIREWALL_DIR.is_dir(),
            f"Firewall directory missing: {FIREWALL_DIR}",
        )
    def test_required_firewall_files_exist(self):
        missing = [
            name
            for name in REQUIRED_FILES
            if not (FIREWALL_DIR / name).is_file()
        ]
        self.assertEqual(
            missing,
            [],
            f"Required firewall files are missing: {missing}",
        )
    def test_required_test_files_exist(self):
        tests_dir = FIREWALL_DIR / "tests"
        self.assertTrue(tests_dir.is_dir(), "Firewall tests directory missing")
        missing = [
            name
            for name in REQUIRED_TEST_FILES
            if not (tests_dir / name).is_file()
        ]
        self.assertEqual(
            missing,
            [],
            f"Required test files are missing: {missing}",
        )
    def test_firewall_config_is_valid_json(self):
        config_path = FIREWALL_DIR / "firewall_config.json"
        if not config_path.is_file():
            self.skipTest("Firewall configuration file is missing")
        try:
            with config_path.open("r", encoding="utf-8") as file:
                config = json.load(file)
        except (OSError, json.JSONDecodeError) as exc:
            self.fail(f"Firewall configuration is not valid JSON: {exc}")
        self.assertIsInstance(config, dict)
    def test_config_keeps_system_rule_changes_disabled(self):
        config_path = FIREWALL_DIR / "firewall_config.json"
        if not config_path.is_file():
            self.skipTest("Firewall configuration file is missing")
        with config_path.open("r", encoding="utf-8") as file:
            config = json.load(file)
        system_firewall = config.get("system_firewall", {})
        self.assertIsInstance(system_firewall, dict)
        self.assertIs(
            system_firewall.get("modify_system_rules"),
            False,
            "System firewall rule modification must remain disabled by default",
        )
if __name__ == "__main__":
    unittest.main(verbosity=2)