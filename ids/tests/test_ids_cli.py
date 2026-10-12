"""Tests for the Tamanna AI IDS command-line interface."""
import io
import json
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch
from ids import ids_cli
class TestIDSCLI(unittest.TestCase):
    """Verify CLI commands and their JSON output."""
    def run_cli(self, arguments):
        """Run a CLI command and capture its standard output."""
        output = io.StringIO()
        with redirect_stdout(output):
            result = ids_cli.main(arguments)
        return result, output.getvalue()
    @patch("ids.ids_cli.load_config")
    def test_config_command(self, mock_load_config):
        expected = {
            "project": "Tamanna AI",
            "mode": "monitor_only",
            "enabled": True,
        }
        mock_load_config.return_value = expected
        result, output = self.run_cli(["config"])
        self.assertIsNone(result)
        self.assertEqual(json.loads(output), expected)
        mock_load_config.assert_called_once()
    @patch("ids.ids_cli.run_health_check")
    def test_health_command(self, mock_health_check):
        expected = {
            "status": "healthy",
            "mode": "monitor_only",
            "system_firewall_modified": False,
        }
        mock_health_check.return_value = expected
        result, output = self.run_cli(["health"])
        self.assertIsNone(result)
        self.assertEqual(json.loads(output), expected)
        mock_health_check.assert_called_once()
    @patch("ids.ids_cli.generate_report")
    def test_report_command(self, mock_generate_report):
        expected = {
            "project": "Tamanna AI",
            "status": "healthy",
            "system_firewall_modified": False,
        }
        mock_generate_report.return_value = expected
        result, output = self.run_cli(["report"])
        self.assertIsNone(result)
        self.assertEqual(json.loads(output), expected)
        mock_generate_report.assert_called_once()
    def test_help_command(self):
        with self.assertRaises(SystemExit) as context:
            ids_cli.main(["--help"])
        self.assertEqual(context.exception.code, 0)
if __name__ == "__main__":
    unittest.main()