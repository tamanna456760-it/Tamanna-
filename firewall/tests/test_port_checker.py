"""Tests for Tamanna AI firewall port checker."""
import unittest
from unittest.mock import patch
from firewall.port_checker import get_listening_ports
class TestPortChecker(unittest.TestCase):
    def test_port_checker_returns_a_collection(self):
        """Port checker should return a collection of listening ports."""
        result = get_listening_ports()
        self.assertIsInstance(result, (list, tuple, set))
    @patch("firewall.port_checker.subprocess.run")
    def test_port_checker_handles_command_failure(self, mock_run):
        """A failed system command should be handled safely."""
        mock_run.side_effect = OSError("Command unavailable")
        try:
            result = get_listening_ports()
        except OSError:
            self.fail("Port checker should handle an unavailable command.")
        self.assertIsInstance(result, (list, tuple, set))
if __name__ == "__main__":
    unittest.main()