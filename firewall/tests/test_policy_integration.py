"""Integration tests for Tamanna AI firewall policy validation."""
import unittest
from firewall.access_control import evaluate_access
from firewall.policy_validator import validate_policy
class TestPolicyIntegration(unittest.TestCase):
    def setUp(self):
        self.policy = {
            "mode": "audit_only",
            "default_policy": "deny",
            "allowed_ips": ["127.0.0.1", "::1"],
            "blocked_ips": ["192.0.2.10"],
            "allowed_ports": [8000],
        }
    def test_valid_policy_is_accepted(self):
        """A valid audit-only policy should pass validation."""
        result = validate_policy(self.policy)
        if isinstance(result, dict):
            self.assertTrue(result.get("valid", result.get("ok", False)))
        else:
            self.assertTrue(result)
    def test_loopback_access_is_allowed_by_policy(self):
        """Configured loopback access should be allowed."""
        result = evaluate_access(
            client_ip="127.0.0.1",
            port=8000,
            policy=self.policy,
        )
        self.assertTrue(result.allowed)
    def test_unlisted_ip_is_denied_by_default(self):
        """An unlisted client should be denied by the default-deny policy."""
        result = evaluate_access(
            client_ip="192.0.2.25",
            port=8000,
            policy=self.policy,
        )
        self.assertFalse(result.allowed)
    def test_blocked_ip_is_denied(self):
        """An explicitly blocked client should not be allowed."""
        result = evaluate_access(
            client_ip="192.0.2.10",
            port=8000,
            policy=self.policy,
        )
        self.assertFalse(result.allowed)
if __name__ == "__main__":
    unittest.main()