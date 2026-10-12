"""Schema checks for Tamanna AI firewall configuration."""
import json
import unittest
from pathlib import Path
CONFIG_PATH = (
    Path(__file__).resolve().parents[2]
    / "firewall"
    / "firewall_config.json"
)
class TestFirewallConfigSchema(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with CONFIG_PATH.open("r", encoding="utf-8") as file:
            cls.config = json.load(file)
    def test_mode_is_supported(self):
        self.assertIn(
            self.config.get("mode"),
            {"audit_only", "monitor", "enforce"},
        )
    def test_default_policy_is_supported(self):
        self.assertIn(
            self.config.get("default_policy"),
            {"allow", "deny"},
        )
    def test_allowed_ips_is_a_list(self):
        allowed_ips = self.config.get("allowed_ips", [])
        self.assertIsInstance(allowed_ips, list)
        for address in allowed_ips:
            with self.subTest(address=address):
                self.assertIsInstance(address, str)
                self.assertTrue(address.strip())
    def test_allowed_ports_are_valid_integers(self):
        ports = self.config.get("allowed_ports", [])
        self.assertIsInstance(ports, list)
        for port in ports:
            with self.subTest(port=port):
                self.assertIsInstance(port, int)
                self.assertNotIsInstance(port, bool)
                self.assertGreaterEqual(port, 1)
                self.assertLessEqual(port, 65535)
    def test_rate_limit_configuration_is_an_object_if_present(self):
        for key in ("rate_limit", "rate_limits", "api_rate_limit"):
            if key in self.config:
                self.assertIsInstance(self.config[key], dict)
if __name__ == "__main__":
    unittest.main()