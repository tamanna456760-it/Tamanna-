"""Tests for Tamanna AI firewall port-checker robustness."""
import unittest
from unittest.mock import patch
from firewall.port_checker import get_listening_ports
class TestPortCheckerParsing(unittest.TestCase):
    @patch("firewall.port_checker.subprocess.run")
    def test_empty_output_returns_collection(self, mock_run):
        mock_run.return_value.stdout = ""
        mock_run.return_value.returncode = 0
        result = get_listening_ports()
        self.assertIsInstance(result, (list, tuple, set))
    @patch("firewall.port_checker.subprocess.run")
    def test_command_failure_is_handled(self, mock_run):
        mock_run.side_effect = OSError("ss command unavailable")
        try:
            result = get_listening_ports()
        except OSError:
            self.fail("Port checker should handle a missing ss command.")
        self.assertIsInstance(result, (list, tuple, set))
    @patch("firewall.port_checker.subprocess.run")
    def test_listening_port_output_is_processed(self, mock_run):
        mock_run.return_value.stdout = (
            "LISTEN 0 128 127.0.0.1:8000 0.0.0.0:*\n"
        )
        mock_run.return_value.returncode = 0
        result = get_listening_ports()
        self.assertIsInstance(result, (list, tuple, set))
if __name__ == "__main__":
    unittest.main()