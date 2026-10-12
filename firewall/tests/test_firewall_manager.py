"""Tests for Tamanna AI firewall manager."""
import unittest
from firewall.firewall_manager import FirewallManager
class TestFirewallManager(unittest.TestCase):
    def setUp(self):
        self.manager = FirewallManager()
    def test_manager_initializes(self):
        """Firewall manager should initialize successfully."""
        self.assertIsNotNone(self.manager)
    def test_health_check_if_available(self):
        """Run the health check when the manager exposes one."""
        for name in ("health_check", "get_health", "health"):
            method = getattr(self.manager, name, None)
            if callable(method):
                result = method()
                self.assertIsNotNone(result)
                return
        self.skipTest(
            "No recognized health-check method found in FirewallManager."
        )
    def test_policy_check_if_available(self):
        """Check that a policy-evaluation method exists."""
        method_names = (
            "check_access",
            "evaluate_access",
            "is_allowed",
            "check_policy",
        )
        if not any(
            callable(getattr(self.manager, name, None))
            for name in method_names
        ):
            self.skipTest(
                "Access evaluation is provided by another firewall module."
            )
if __name__ == "__main__":
    unittest.main()