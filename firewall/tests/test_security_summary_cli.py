"""
Tamanna AI Firewall - Security Summary CLI Tests
Owner: HM INSAN ALI
"""
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from firewall.security_summary_cli import main
def create_report(path, total=2, high_risk=0):
    report = {
        "project": "Tamanna AI",
        "owner": "HM INSAN ALI",
        "generated_at": "2026-10-12T12:00:00+00:00",
        "analysis": {
            "total_events": total,
            "high_risk_events": high_risk,
        },
        "system_firewall_modified": False,
    }
    path.write_text(json.dumps(report), encoding="utf-8")
class TestSecuritySummaryCLI(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.root = Path(self.temp_dir.name)
        self.report_path = self.root / "event_report.json"
        self.output_path = self.root / "summary.json"
    def run_cli(self, args):
        output = StringIO()
        with redirect_stdout(output):
            exit_code = main(args)
        return exit_code, output.getvalue()
    def test_valid_report_prints_json(self):
        create_report(self.report_path)
        exit_code, output = self.run_cli([
            "--report", str(self.report_path),
        ])
        result = json.loads(output)
        self.assertEqual(exit_code, 0)
        self.assertTrue(result["report_valid"])
        self.assertEqual(result["project"], "Tamanna AI")
    def test_output_option_saves_summary(self):
        create_report(self.report_path)
        exit_code, _ = self.run_cli([
            "--report", str(self.report_path),
            "--output", str(self.output_path),
        ])
        self.assertEqual(exit_code, 0)
        self.assertTrue(self.output_path.is_file())
        saved = json.loads(
            self.output_path.read_text(encoding="utf-8")
        )
        self.assertEqual(saved["total_events"], 2)
    def test_strict_mode_fails_for_high_risk_events(self):
        create_report(self.report_path, total=3, high_risk=1)
        exit_code, _ = self.run_cli([
            "--report", str(self.report_path),
            "--strict",
        ])
        self.assertEqual(exit_code, 1)
    def test_strict_mode_fails_for_invalid_report(self):
        self.report_path.write_text(
            "{invalid json",
            encoding="utf-8",
        )
        exit_code, _ = self.run_cli([
            "--report", str(self.report_path),
            "--strict",
        ])
        self.assertEqual(exit_code, 1)
    def test_non_strict_mode_handles_missing_report(self):
        exit_code, output = self.run_cli([
            "--report", str(self.report_path),
        ])
        result = json.loads(output)
        self.assertEqual(exit_code, 0)
        self.assertFalse(result["report_valid"])
    def test_firewall_rules_are_not_modified(self):
        create_report(self.report_path)
        _, output = self.run_cli([
            "--report", str(self.report_path),
        ])
        result = json.loads(output)
        self.assertFalse(result["system_firewall_modified"])
if __name__ == "__main__":
    unittest.main(verbosity=2)