"""Import smoke tests for Tamanna AI firewall modules."""
import importlib
import unittest
MODULES = (
    "firewall",
    "firewall.firewall_manager",
    "firewall.port_checker",
    "firewall.access_control",
    "firewall.audit_log",
    "firewall.rate_limiter",
    "firewall.threat_detector",
    "firewall.security_monitor",
    "firewall.api_protection",
    "firewall.policy_validator",
    "firewall.defense_score",
)
class TestFirewallImports(unittest.TestCase):
    def test_firewall_modules_import(self):
        """Every listed module should import without an exception."""
        for module_name in MODULES:
            with self.subTest(module=module_name):
                module = importlib.import_module(module_name)
                self.assertIsNotNone(module)
if __name__ == "__main__":
    unittest.main()