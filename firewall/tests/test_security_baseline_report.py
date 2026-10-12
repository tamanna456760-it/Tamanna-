"""
Tamanna AI Firewall - Security Baseline Report Tests
Owner: HM INSAN ALI
"""
import json
import tempfile
import unittest
from pathlib import Path
from firewall.security_baseline_report import generate_report
class TestSecurityBaselineReport(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.root = Path(self.temp_dir.name)
        self.config_path = self.root / "firewall_config.json"
        self.report_path = self.root / "reports" / "baseline.json"
        self.config = {
            "mode": "audit_only",
            "default_policy": "deny",
            "allowed_ips": ["127.0.0.1", "::1"],
            "allowed_ports": [],
            "system_firewall": {
                "modify_system_rules": False
            },
        }
        self.config_path.write_text(
            json.dumps(self.config),
            encoding="utf-8",
        )
    def test_report_is_created(self):
        report = generate_report(
            config_path=self.config_path,
            report_path=self.report_path,
        )
        self.assertTrue(self.report_path.is_file())
        self.assertEqual(report["project"], "Tamanna AI")
        self.assertEqual(report["owner"], "HM INSAN ALI")
    def test_saved_report_contains_baseline_results(self):
        generate_report(
            config_path=self.config_path,
            report_path=self.report_path,
        )
        saved = json.loads(
            self.report_path.read_text(encoding="utf-8")
        )
        self.assertIn("generated_at", saved)
        self.assertIn("baseline", saved)
        self.assertEqual(saved["baseline"]["status"], "PASS")
    def test_report_directory_is_created(self):
        self.assertFalse(self.report_path.parent.exists())
        generate_report(
            config_path=self.config_path,
            report_path=self.report_path,
        )
        self.assertTrue(self.report_path.parent.is_dir())
    def test_invalid_json_is_rejected(self):
        self.config_path.write_text(
            "{invalid-json",
            encoding="utf-8",
        )
        with self.assertRaises(json.JSONDecodeError):
            generate_report(
                config_path=self.config_path,
                report_path=self.report_path,
            )
    def test_system_rules_are_not_modified(self):
        generate_report(
            config_path=self.config_path,
            report_path=self.report_path,
        )
        saved = json.loads(
            self.report_path.read_text(encoding="utf-8")
        )
        self.assertFalse(
            saved["baseline"]["system_rules_modified"]
        )
if __name__ == "__main__":
    unittest.main(verbosity=2)