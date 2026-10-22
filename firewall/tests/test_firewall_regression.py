"""Regression tests for Tamanna AI firewall modules."""
import unittest
from firewall.access_control import evaluate_access
from firewall.firewall_manager import FirewallManager
from firewall.rate_limiter import RateLimiter
from firewall.security_monitor import SecurityMonitor
from firewall.threat_detector import ThreatDetector
class TestFirewallRegression(unittest.TestCase):
    def test_firewall_manager_initializes(self):
        manager = FirewallManager()
        self.assertIsNotNone(manager)
    def test_security_monitor_initializes(self):
        monitor = SecurityMonitor()
        self.assertIsNotNone(monitor)
    def test_threat_detector_initializes(self):
        detector = ThreatDetector()
        self.assertIsNotNone(detector)
    def test_rate_limiter_initializes(self):
        limiter = RateLimiter()
        self.assertIsNotNone(limiter)
    def test_default_deny_policy(self):
        policy = {
            "mode": "audit_only",
            "default_policy": "deny",
            "allowed_ips": ["127.0.0.1"],
            "blocked_ips": [],
            "allowed_ports": [8000],
        }
        result = evaluate_access(
            client_ip="192.0.2.50",
            port=8000,
            policy=policy,
        )
        self.assertFalse(result.allowed)
    def test_loopback_access_policy(self):
        policy = {
            "mode": "audit_only",
            "default_policy": "deny",
            "allowed_ips": ["127.0.0.1"],
            "blocked_ips": [],
            "allowed_ports": [8000],
        }
        result = evaluate_access(
            client_ip="127.0.0.1",
            port=8000,
            policy=policy,
        )
        self.assertTrue(result.allowed)
if __name__ == "__main__":
    unittest.main()