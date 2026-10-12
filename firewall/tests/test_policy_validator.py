"""
Tamanna AI — Security Policy Validator Tests
Owner: HM INSAN ALI
Run from the repository root:
    python -m unittest firewall.tests.test_policy_validator -v
Tests are local-only and do not change system firewall rules.
"""
import unittest
from firewall.policy_validator import validate_policy
def valid_policy():
    """Return a minimal, safe test policy."""
    return {
        "mode": "audit_only",
        "default_policy": "deny",
        "default_deny": True,
        "allowed_ips": ["127.0.0.1", "::1"],
        "blocked_ips": [],
        "allowed_ports": [8000, 443],
        "api_protection": {
            "max_body_bytes": 1048576,
        },
        "rate_limits": {
            "requests_per_minute": 60,
            "burst": 10,
        },
        "system_firewall": {
            "modify_system_rules": False,
            "explicit_approval_required": True,
        },
    }
class TestValidPolicies(unittest.TestCase):
    def test_safe_audit_policy_is_valid(self):
        result = validate_policy(valid_policy())
        self.assertTrue(result["valid"], result["errors"])
        self.assertEqual(result["errors"], [])
    def test_ipv6_loopback_is_valid(self):
        config = valid_policy()
        config["allowed_ips"] = ["::1"]
        result = validate_policy(config)
        self.assertTrue(result["valid"], result["errors"])
class TestInvalidRoot(unittest.TestCase):
    def test_list_root_is_rejected(self):
        result = validate_policy([])
        self.assertFalse(result["valid"])
        self.assertTrue(
            any(error["code"] == "invalid_root"
                for error in result["errors"])
        )
    def test_string_root_is_rejected(self):
        result = validate_policy("not a configuration")
        self.assertFalse(result["valid"])
class TestModeValidation(unittest.TestCase):
    def test_unknown_mode_is_rejected(self):
        config = valid_policy()
        config["mode"] = "unrestricted"
        result = validate_policy(config)
        self.assertFalse(result["valid"])
        self.assertTrue(
            any(error["code"] == "invalid_mode"
                for error in result["errors"])
        )
    def test_enforce_mode_warns_about_integration(self):
        config = valid_policy()
        config["mode"] = "enforce"
        result = validate_policy(config)
        self.assertTrue(result["valid"], result["errors"])
        self.assertTrue(
            any(
                warning["code"] == "enforcement_not_verified"
                for warning in result["warnings"]
            )
        )
class TestDefaultPolicy(unittest.TestCase):
    def test_default_deny_is_accepted(self):
        config = valid_policy()
        config["default_policy"] = "deny"
        result = validate_policy(config)
        self.assertTrue(result["valid"], result["errors"])
    def test_default_allow_produces_warning(self):
        config = valid_policy()
        config["default_policy"] = "allow"
        result = validate_policy(config)
        self.assertTrue(result["valid"], result["errors"])
        self.assertTrue(
            any(
                warning["code"] == "permissive_default"
                for warning in result["warnings"]
            )
        )
    def test_invalid_default_policy_is_rejected(self):
        config = valid_policy()
        config["default_policy"] = "sometimes"
        result = validate_policy(config)
        self.assertFalse(result["valid"])
class TestAddressValidation(unittest.TestCase):
    def test_invalid_allowed_ip_is_rejected(self):
        config = valid_policy()
        config["allowed_ips"] = ["not-an-ip"]
        result = validate_policy(config)
        self.assertFalse(result["valid"])
        self.assertTrue(
            any(error["code"] == "invalid_ip"
                for error in result["errors"])
        )
    def test_invalid_blocked_ip_is_rejected(self):
        config = valid_policy()
        config["blocked_ips"] = ["999.999.999.999"]
        result = validate_policy(config)
        self.assertFalse(result["valid"])
    def test_allowed_ips_must_be_a_list(self):
        config = valid_policy()
        config["allowed_ips"] = "127.0.0.1"
        result = validate_policy(config)
        self.assertFalse(result["valid"])
class TestPortValidation(unittest.TestCase):
    def test_port_zero_is_rejected(self):
        config = valid_policy()
        config["allowed_ports"] = [0]
        result = validate_policy(config)
        self.assertFalse(result["valid"])
    def test_port_above_range_is_rejected(self):
        config = valid_policy()
        config["allowed_ports"] = [65536]
        result = validate_policy(config)
        self.assertFalse(result["valid"])
    def test_boolean_is_not_a_valid_port(self):
        config = valid_policy()
        config["allowed_ports"] = [True]
        result = validate_policy(config)
        self.assertFalse(result["valid"])
class TestRateLimitValidation(unittest.TestCase):
    def test_zero_request_limit_is_rejected(self):
        config = valid_policy()
        config["rate_limits"]["requests_per_minute"] = 0
        result = validate_policy(config)
        self.assertFalse(result["valid"])
    def test_negative_burst_is_rejected(self):
        config = valid_policy()
        config["rate_limits"]["burst"] = -1
        result = validate_policy(config)
        self.assertFalse(result["valid"])
    def test_boolean_rate_limit_is_rejected(self):
        config = valid_policy()
        config["rate_limits"]["burst"] = True
        result = validate_policy(config)
        self.assertFalse(result["valid"])
class TestRequestSizeValidation(unittest.TestCase):
    def test_zero_body_limit_is_rejected(self):
        config = valid_policy()
        config["api_protection"]["max_body_bytes"] = 0
        result = validate_policy(config)
        self.assertFalse(result["valid"])
    def test_invalid_api_protection_section_is_rejected(self):
        config = valid_policy()
        config["api_protection"] = []
        result = validate_policy(config)
        self.assertFalse(result["valid"])
class TestSystemFirewallSafety(unittest.TestCase):
    def test_system_rule_changes_remain_disabled(self):
        config = valid_policy()
        result = validate_policy(config)
        self.assertTrue(result["valid"], result["errors"])
        self.assertFalse(
            config["system_firewall"]["modify_system_rules"]
        )
    def test_rule_changes_without_approval_are_rejected(self):
        config = valid_policy()
        config["system_firewall"]["modify_system_rules"] = True
        config["system_firewall"]["explicit_approval_required"] = False
        result = validate_policy(config)
        self.assertFalse(result["valid"])
        self.assertTrue(
            any(
                error["code"] == "unsafe_firewall_change"
                for error in result["errors"]
            )
        )
    def test_rule_changes_with_approval_produce_warning(self):
        config = valid_policy()
        config["system_firewall"]["modify_system_rules"] = True
        config["system_firewall"]["explicit_approval_required"] = True
        result = validate_policy(config)
        self.assertTrue(result["valid"], result["errors"])
        self.assertTrue(
            any(
                warning["code"] == "approval_required"
                for warning in result["warnings"]
            )
        )
if __name__ == "__main__":
    unittest.main(verbosity=2)