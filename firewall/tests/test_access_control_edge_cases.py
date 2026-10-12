"""Edge-case tests for Tamanna AI firewall access control."""
import unittest
from firewall.access_control import evaluate_access
class TestAccessControlEdgeCases(unittest.TestCase):
    def setUp(self):
        self.policy = {
            "mode": "audit_only",
            "default_policy": "deny",
            "allowed_ips": ["127.0.0.1", "::1"],
            "blocked_ips": ["192.0.2.10"],
            "allowed_ports": [8000],
        }
    def test_blocked_ip_is_denied(self):
        result = evaluate_access(
            client_ip="192.0.2.10",
            port=8000,
            policy=self.policy,
        )
        self.assertFalse(result.allowed)
    def test_unknown_ip_is_denied(self):
        result = evaluate_access(
            client_ip="192.0.2.25",
            port=8000,
            policy=self.policy,
        )
        self.assertFalse(result.allowed)
    def test_unlisted_port_is_denied(self):
        result = evaluate_access(
            client_ip="127.0.0.1",
            port=9000,
            policy=self.policy,
        )
        self.assertFalse(result.allowed)
    def test_allowed_loopback_ip_and_port(self):
        result = evaluate_access(
            client_ip="127.0.0.1",
            port=8000,
            policy=self.policy,
        )
        self.assertTrue(result.allowed)
    def test_invalid_port_is_denied(self):
        for port in (-1, 0, 65536):
            with self.subTest(port=port):
                result = evaluate_access(
                    client_ip="127.0.0.1",
                    port=port,
                    policy=self.policy,
                )
                self.assertFalse(result.allowed)
if __name__ == "__main__":
    unittest.main()