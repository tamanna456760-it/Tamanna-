"""
Tamanna AI Firewall - Security Status Tests
Owner: HM INSAN ALI
"""
import json
import tempfile
import unittest
from pathlib import Path
from firewall.security_status import (
    check_security_status,
    save_security_status,
)
def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data), encoding="utf-8")
class TestSecurityStatus(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.root = Path(self.temp_dir.name)
    def create_valid_files(self):
        write_json(
            self.root / "firewall_config.json",
            {
                "mode": "audit_only",
                "allowed_ips": ["127.0.0.1"],
                "allowed_ports": [],
            },
        )
        write_json(
            self.root / "reports" / "event_report.json",
            {"project": "Tamanna AI"},
        )
        write_json(
            self.root / "reports" / "security_summary.json",
            {"project": "Tamanna AI"},
        )
    def test_all_required_files_report_ready_for_review(self):
        self.create_valid_files()
        result = check_security_status(self.root)
        self.assertEqual(result["status"], "READY_FOR_REVIEW")
        self.assertTrue(result["checks"]["config_valid"])
        self.assertEqual(result["config_mode"], "audit_only")
    def test_missing_files_report_incomplete(self):
        result = check_security_status(self.root)
        self.assertEqual(result["status"], "INCOMPLETE")
        self.assertFalse(result["checks"]["config_exists"])
        self.assertFalse(result["checks"]["event_report_exists"])
    def test_invalid_json_config_is_rejected(self):
        config = self.root / "firewall_config.json"
        config.write_text("{invalid json", encoding="utf-8")
        result = check_security_status(self.root)
        self.assertFalse(result["checks"]["config_valid"])
        self.assertTrue(result["config_errors"])
        self.assertEqual(result["status"], "INCOMPLETE")
    def test_unsupported_mode_is_rejected(self):
        write_json(
            self.root / "firewall_config.json",
            {
                "mode": "unknown",
                "allowed_ips": [],
                "allowed_ports": [],
            },
        )
        result = check_security_status(self.root)
        self.assertFalse(result["checks"]["config_valid"])
    def test_wrong_allowed_ips_type_is_rejected(self):
        write_json(
            self.root / "firewall_config.json",
            {
                "mode": "audit_only",
                "allowed_ips": "127.0.0.1",
                "allowed_ports": [],
            },
        )
        result = check_security_status(self.root)
        self.assertFalse(result["checks"]["config_valid"])
    def test_status_is_saved_as_json(self):
        self.create_valid_files()
        output = self.root / "reports" / "security_status.json"
        result = save_security_status(output, self.root)
        self.assertTrue(output.is_file())
        saved = json.loads(output.read_text(encoding="utf-8"))
        self.assertEqual(saved["project"], "Tamanna AI")
        self.assertEqual(saved["status"], result["status"])
    def test_status_does_not_claim_to_modify_firewall(self):
        result = check_security_status(self.root)
        self.assertFalse(result["system_firewall_modified"])
    def test_wrong_allowed_ports_type_is_rejected(self):
        write_json(
            self.root / "firewall_config.json",
            {
                "mode": "audit_only",
                "allowed_ips": [],
                "allowed_ports": "8000",
            },
        )
        result = check_security_status(self.root)
        self.assertFalse(result["checks"]["config_valid"])
if __name__ == "__main__":
    unittest.main(verbosity=2)