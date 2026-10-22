"""
Tamanna AI Firewall - Health Report Tests
Owner: HM INSAN ALI
"""
import json
import tempfile
import unittest
from pathlib import Path
from firewall.health_report import save_health_report
class TestHealthReport(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.root = Path(self.temp_dir.name)
        self.firewall_dir = self.root / "firewall"
        self.firewall_dir.mkdir()
        self.report_path = self.root / "reports" / "health.json"
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
        for name in required_files:
            path = self.firewall_dir / name
            if name == "firewall_config.json":
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
    def test_report_is_saved(self):
        report = save_health_report(
            report_path=self.report_path,
            firewall_dir=self.firewall_dir,
        )
        self.assertTrue(self.report_path.is_file())
        self.assertEqual(report["project"], "Tamanna AI")
        self.assertEqual(report["owner"], "HM INSAN ALI")
    def test_saved_json_matches_returned_report(self):
        report = save_health_report(
            report_path=self.report_path,
            firewall_dir=self.firewall_dir,
        )
        saved = json.loads(
            self.report_path.read_text(encoding="utf-8")
        )
        self.assertEqual(saved, report)
        self.assertIn("generated_at", saved)
        self.assertIn("health", saved)
    def test_report_directory_is_created(self):
        self.assertFalse(self.report_path.parent.exists())
        save_health_report(
            report_path=self.report_path,
            firewall_dir=self.firewall_dir,
        )
        self.assertTrue(self.report_path.parent.is_dir())
    def test_system_firewall_is_not_modified(self):
        report = save_health_report(
            report_path=self.report_path,
            firewall_dir=self.firewall_dir,
        )
        self.assertFalse(report["system_firewall_modified"])
    def test_missing_files_are_reported(self):
        (self.firewall_dir / "rate_limiter.py").unlink()
        report = save_health_report(
            report_path=self.report_path,
            firewall_dir=self.firewall_dir,
        )
        self.assertEqual(
            report["health"]["status"],
            "NEEDS_ATTENTION",
        )
        self.assertGreater(
            report["health"]["missing_files"],
            0,
        )
if __name__ == "__main__":
    unittest.main(verbosity=2)