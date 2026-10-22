"""
Tamanna AI Firewall - Doctor Tests
Owner: HM INSAN ALI
"""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from firewall.doctor import run_diagnostics
class TestFirewallDoctor(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.root = Path(self.temp_dir.name)
    def write_config(self, config):
        (self.root / "firewall_config.json").write_text(
            json.dumps(config),
            encoding="utf-8",
        )
    def create_required_files(self):
        for filename in (
            "firewall_config.json",
            "firewall_manager.py",
            "access_control.py",
            "audit_log.py",
            "security_status.py",
        ):
            path = self.root / filename
            if filename == "firewall_config.json":
                self.write_config({
                    "mode": "audit_only",
                    "allowed_ips": ["127.0.0.1"],
                    "allowed_ports": [],
                })
            else:
                path.write_text("# test placeholder\n", encoding="utf-8")
    def test_missing_files_are_reported(self):
        result = run_diagnostics(self.root)
        self.assertEqual(result["status"], "ISSUES_FOUND")
        self.assertTrue(result["checks_failed"] > 0)
        self.assertTrue(
            any("Missing required file" in error for error in result["errors"])
        )
    def test_invalid_config_is_reported(self):
        self.create_required_files()
        self.write_config({
            "mode": "unknown",
            "allowed_ips": [],
            "allowed_ports": [],
        })
        result = run_diagnostics(self.root)
        self.assertTrue(
            any(
                "failed basic validation" in error
                for error in result["errors"]
            )
        )
    def test_invalid_json_is_reported(self):
        self.create_required_files()
        (self.root / "firewall_config.json").write_text(
            "{broken",
            encoding="utf-8",
        )
        result = run_diagnostics(self.root)
        self.assertTrue(
            any("Unable to read firewall configuration" in error
                for error in result["errors"])
        )
    def test_import_error_is_reported(self):
        self.create_required_files()
        with patch(
            "firewall.doctor.importlib.import_module",
            side_effect=ImportError("simulated import error"),
        ):
            result = run_diagnostics(self.root)
        self.assertTrue(
            any("Import failed" in error for error in result["errors"])
        )
        self.assertEqual(result["status"], "ISSUES_FOUND")
    def test_result_has_expected_fields(self):
        result = run_diagnostics(self.root)
        self.assertEqual(result["project"], "Tamanna AI")
        self.assertEqual(result["owner"], "HM INSAN ALI")
        self.assertIn("checks", result)
        self.assertIn("checks_passed", result)
        self.assertIn("checks_failed", result)
    def test_diagnostics_do_not_claim_firewall_changes(self):
        result = run_diagnostics(self.root)
        self.assertFalse(result["system_firewall_modified"])
if __name__ == "__main__":
    unittest.main(verbosity=2)