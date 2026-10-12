"""
Tamanna AI — Access Control Tests
Owner: HM INSAN ALI
Run from the repository root:
    python -m unittest firewall.tests.test_access_control -v
Local policy tests only. No network traffic is sent.
"""
import unittest
from firewall.access_control import evaluate_access
def make_policy(**overrides):
    policy = {
        "default_policy": "deny",
        "allowed_ips": ["127.0.0.1", "::1"],
        "blocked_ips": [],
        "allowed_ports": [8000, 443],
    }
    policy.update(overrides)
    return policy
class TestAccessControl(unittest.TestCase):
    def test_allowed_loopback_ip_and_port(self):
        result = evaluate_access(
            client_ip="127.0.0.1",
            port=8000,
            policy=make_policy(),
        )
        self.assertTrue(result.allowed)
    def test_unknown_ip_is_denied(self):
        result = evaluate_access(
            client_ip="203.0.113.10",
            port=443,
            policy=make_policy(),
        )
        self.assertFalse(result.allowed)
    def test_unlisted_port_is_denied(self):
        result = evaluate_access(
            client_ip="127.0.0.1",
            port=9000,
            policy=make_policy(),
        )
        self.assertFalse(result.allowed)
    def test_blocked_ip_is_denied_even_if_allowed(self):
        result = evaluate_access(
            client_ip="127.0.0.1",
            port=8000,
            policy=make_policy(
                blocked_ips=["127.0.0.1"],
            ),
        )
        self.assertFalse(result.allowed)
    def test_ipv6_loopback_can_be_allowed(self):
        result = evaluate_access(
            client_ip="::1",
            port=443,
            policy=make_policy(),
        )
        self.assertTrue(result.allowed)
    def test_invalid_ip_is_denied(self):
        result = evaluate_access(
            client_ip="not-an-ip",
            port=8000,
            policy=make_policy(),
        )
        self.assertFalse(result.allowed)
    def test_invalid_port_is_denied(self):
        result = evaluate_access(
            client_ip="127.0.0.1",
            port=70000,
            policy=make_policy(),
        )
        self.assertFalse(result.allowed)
    def test_boolean_port_is_denied(self):
        result = evaluate_access(
            client_ip="127.0.0.1",
            port=True,
            policy=make_policy(),
        )
        self.assertFalse(result.allowed)
    def test_default_deny_policy_is_preserved(self):
        result = evaluate_access(
            client_ip="198.51.100.25",
            port=8000,
            policy=make_policy(),
        )
        self.assertFalse(result.allowed)
if __name__ == "__main__":
    unittest.main(verbosity=2)