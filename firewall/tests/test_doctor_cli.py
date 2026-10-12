"""Tests for the Tamanna AI Firewall doctor CLI.
Owner: HM INSAN ALI
"""
import json
import unittest
from unittest.mock import patch
from firewall import doctor_cli
class TestDoctorCLI(unittest.TestCase):
    @patch(
        "firewall.doctor_cli.run_diagnostics",
        return_value={
            "project": "Tamanna AI",
            "owner": "HM INSAN ALI",
            "status": "OK",
            "checks": [],
            "system_firewall_modified": False,
        },
    )
    def test_successful_diagnostics(self, mock_diagnostics):
        with patch("sys.argv", ["doctor_cli"]):
            with patch("builtins.print") as mock_print:
                result = doctor_cli.main()
        self.assertEqual(result, 0)
        mock_diagnostics.assert_called_once_with(base_dir=None)
        printed_json = mock_print.call_args.args[0]
        report = json.loads(printed_json)
        self.assertEqual(report["status"], "OK")
        self.assertFalse(report["system_firewall_modified"])
    @patch(
        "firewall.doctor_cli.run_diagnostics",
        return_value={"status": "ISSUES_FOUND"},
    )
    def test_strict_mode_returns_failure_for_issues(
        self, mock_diagnostics
    ):
        with patch("sys.argv", ["doctor_cli", "--strict"]):
            with patch("builtins.print"):
                result = doctor_cli.main()
        self.assertEqual(result, 1)
    @patch(
        "firewall.doctor_cli.run_diagnostics",
        side_effect=OSError("Cannot read project files"),
    )
    def test_diagnostic_error_returns_two(self, mock_diagnostics):
        with patch("sys.argv", ["doctor_cli"]):
            with patch("builtins.print") as mock_print:
                result = doctor_cli.main()
        self.assertEqual(result, 2)
        error_report = json.loads(mock_print.call_args.args[0])
        self.assertEqual(error_report["status"], "ERROR")
        self.assertFalse(error_report["system_firewall_modified"])
    @patch(
        "firewall.doctor_cli.run_diagnostics",
        return_value={"status": "ISSUES_FOUND"},
    )
    def test_non_strict_mode_allows_issue_report(
        self, mock_diagnostics
    ):
        with patch("sys.argv", ["doctor_cli"]):
            with patch("builtins.print"):
                result = doctor_cli.main()
        self.assertEqual(result, 0)
if __name__ == "__main__":
    unittest.main()