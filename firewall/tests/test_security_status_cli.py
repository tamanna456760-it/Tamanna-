"""
Tamanna AI Firewall - Security Status CLI Tests
Owner: HM INSAN ALI
"""
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from firewall.security_status_cli import main
def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data), encoding="utf-8")
class TestSecurityStatusCLI(unittest.TestCase):
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
    def run_cli(self, args):
        output = StringIO()
        with redirect_stdout(output):
            code = main(args)
        return code, output.getvalue()
    def test_valid_status_outputs_json(self):
        self.create_valid_files()
        code, output = self.run_cli([
            "--base-dir", str(self.root),
        ])
        result = json.loads(output)
        self.assertEqual(code, 0)
        self.assertEqual(result["status"], "READY_FOR_REVIEW")
    def test_strict_mode_fails_when_files_are_missing(self):
        code, output = self.run_cli([
            "--base-dir", str(self.root),
            "--strict",
        ])
        result = json.loads(output)
        self.assertEqual(code, 1)
        self.assertEqual(result["status"], "INCOMPLETE")
    def test_output_option_saves_json(self):
        self.create_valid_files()
        output_path = self.root / "reports" / "status_cli.json"
        code, output = self.run_cli([
            "--base-dir", str(self.root),
            "--output", str(output_path),
        ])
        self.assertEqual(code, 0)
        self.assertTrue(output_path.is_file())
        saved = json.loads(
            output_path.read_text(encoding="utf-8")
        )
        self.assertEqual(saved["project"], "Tamanna AI")
    def test_strict_mode_fails_for_invalid_config(self):
        write_json(
            self.root / "firewall_config.json",
            {
                "mode": "unknown",
                "allowed_ips": [],
                "allowed_ports": [],
            },
        )
        code, output = self.run_cli([
            "--base-dir", str(self.root),
            "--strict",
        ])
        result = json.loads(output)
        self.assertEqual(code, 1)
        self.assertFalse(result["checks"]["config_valid"])
    def test_firewall_modification_is_not_claimed(self):
        code, output = self.run_cli([
            "--base-dir", str(self.root),
        ])
        result = json.loads(output)
        self.assertEqual(code, 0)
        self.assertFalse(result["system_firewall_modified"])
if __name__ == "__main__":
    unittest.main(verbosity=2)