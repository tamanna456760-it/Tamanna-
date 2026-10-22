"""
Tamanna AI Firewall - Health Check Tests
Owner: HM INSAN ALI
"""
import json
import tempfile
import unittest
from pathlib import Path
from firewall.health_check import run_health_check
class TestHealthCheck(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.root = Path(self.temp_dir.name)
    def create_valid_structure(self):
        required_files = (
            "firewall_config.json",
            "firewall_manager.py",
            "access_control.py",
            "api_protection.py",
            "audit_log.py",
            "rate_limiter.py",
            "threat_detector.py",
            "security_monitor.py",
            "policy_validator.py",
            "security_baseline.py",
        )
        for filename in required_files:
            path = self.root / filename
            if filename == "firewall_config.json":
                path.write_text(
                    json.dumps({
                        "mode": "audit_only",
                        "default_policy": "deny",
                        "system_firewall": {
                            "modify_system_rules": False
                        },
                    }),
                    encoding="utf-8",
                )
            else:
                path.write_text(
                    "# Test fixture only\n",
                    encoding="utf-8",
                )
    def test_complete_structure_is_healthy(self):
        self.create_valid_structure()
        report = run_health_check(self.root)
        self.assertEqual(report["status"], "HEALTHY")
        self.assertEqual(report["missing_files"], 0)
        self.assertEqual(report["configuration_status"], "OK")
    def test_missing_file_requires_attention(self):
        self.create_valid_structure()
        (self.root / "rate_limiter.py").unlink()
        report = run_health_check(self.root)
        self.assertEqual(report["status"], "NEEDS_ATTENTION")
        self.assertGreater(report["missing_files"], 0)
    def test_invalid_json_requires_attention(self):
        self.create_valid_structure()
        (self.root / "firewall_config.json").write_text(
            "{invalid",
            encoding="utf-8",
        )
        report = run_health_check(self.root)
        self.assertEqual(report["status"], "NEEDS_ATTENTION")
        self.assertEqual(report["configuration_status"], "INVALID")
    def test_empty_directory_requires_attention(self):
        report = run_health_check(self.root)
        self.assertEqual(report["status"], "NEEDS_ATTENTION")
        self.assertGreater(report["missing_files"], 0)
    def test_health_check_does_not_claim_to_change_system_rules(self):
        self.create_valid_structure()
        report = run_health_check(self.root)
        self.assertFalse(report["system_firewall_modified"])
    def test_report_contains_timestamp_and_file_details(self):
        self.create_valid_structure()
        report = run_health_check(self.root)
        self.assertIn("checked_at", report)
        self.assertIn("files", report)
        self.assertIsInstance(report["files"], list)
if __name__ == "__main__":
    unittest.main(verbosity=2)