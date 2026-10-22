"""Edge-case tests for Tamanna AI firewall policy validation."""
import unittest
from firewall.policy_validator import validate_policy
class TestPolicyValidatorEdgeCases(unittest.TestCase):
    def test_empty_policy_is_rejected_or_reported_invalid(self):
        result = validate_policy({})
        if isinstance(result, dict):
            self.assertFalse(result.get("valid", result.get("ok", False)))
        else:
            self.assertFalse(bool(result))
    def test_unsupported_mode_is_rejected(self):
        policy = {
            "mode": "unrestricted",
            "default_policy": "deny",
            "allowed_ips": [],
            "allowed_ports": [],
        }
        result = validate_policy(policy)
        if isinstance(result, dict):
            self.assertFalse(result.get("valid", result.get("ok", False)))
        else:
            self.assertFalse(bool(result))
    def test_invalid_port_is_rejected(self):
        policy = {
            "mode": "audit_only",
            "default_policy": "deny",
            "allowed_ips": ["127.0.0.1"],
            "allowed_ports": [8000, 70000],
        }
        result = validate_policy(policy)
        if isinstance(result, dict):
            self.assertFalse(result.get("valid", result.get("ok", False)))
        else:
            self.assertFalse(bool(result))
    def test_invalid_ip_is_rejected(self):
        policy = {
            "mode": "audit_only",
            "default_policy": "deny",
            "allowed_ips": ["not-an-ip-address"],
            "allowed_ports": [8000],
        }
        result = validate_policy(policy)
        if isinstance(result, dict):
            self.assertFalse(result.get("valid", result.get("ok", False)))
        else:
            self.assertFalse(bool(result))
if __name__ == "__main__":
    unittest.main()