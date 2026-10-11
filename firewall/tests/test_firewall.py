"""
Tamanna AI — Firewall Security Tests
Owner: HM INSAN ALI
Run from the repository root:
    python -m unittest firewall.tests.test_firewall -v
These tests use local data only. They do not scan networks or modify
operating-system firewall rules.
"""
import unittest
from firewall.access_control import evaluate_access
from firewall.api_protection import validate_api_request
from firewall.defense_score import calculate_defense_score
from firewall.policy_validator import validate_policy
from firewall.threat_detector import ThreatDetector
class TestPolicyValidator(unittest.TestCase):
    def test_audit_only_policy_is_valid(self):
        result = validate_policy({
            "mode": "audit_only",
            "default_policy": "deny",
            "default_deny": True,
            "allowed_ips": ["127.0.0.1", "::1"],
            "blocked_ips": [],
            "allowed_ports": [],
            "api_protection": {"max_body_bytes": 1048576},
            "rate_limits": {
                "requests_per_minute": 60,
                "burst": 10,
            },
            "system_firewall": {
                "modify_system_rules": False,
                "explicit_approval_required": True,
            },
        })
        self.assertTrue(result["valid"], result["errors"])
    def test_invalid_ip_is_rejected(self):
        result = validate_policy({
            "mode": "audit_only",
            "allowed_ips": ["not-an-ip"],
        })
        self.assertFalse(result["valid"])
        self.assertTrue(
            any(error["code"] == "invalid_ip"
                for error in result["errors"])
        )
    def test_invalid_port_is_rejected(self):
        result = validate_policy({
            "mode": "audit_only",
            "allowed_ports": [70000],
        })
        self.assertFalse(result["valid"])
class TestAPIProtection(unittest.TestCase):
    def test_normal_chat_get_is_allowed(self):
        result = validate_api_request(
            method="GET",
            path="/api/chat",
        )
        self.assertTrue(result.allowed)
    def test_unsupported_method_is_rejected(self):
        result = validate_api_request(
            method="TRACE",
            path="/api/chat",
        )
        self.assertFalse(result.allowed)
        self.assertEqual(result.status_code, 405)
    def test_sensitive_route_requires_authentication(self):
        result = validate_api_request(
            method="GET",
            path="/api/admin/status",
            authenticated=False,
        )
        self.assertFalse(result.allowed)
        self.assertEqual(result.status_code, 401)
    def test_large_body_is_rejected(self):
        result = validate_api_request(
            method="POST",
            path="/api/chat",
            content_type="application/json",
            content_length=2 * 1024 * 1024,
        )
        self.assertFalse(result.allowed)
        self.assertEqual(result.status_code, 413)
    def test_path_traversal_is_rejected(self):
        result = validate_api_request(
            method="GET",
            path="/api/../admin",
        )
        self.assertFalse(result.allowed)
class TestDefenseScore(unittest.TestCase):
    def test_all_passing_checks_score_100(self):
        checks = {
            name: True
            for name in (
                "policy_validation",
                "audit_log_integrity",
                "api_protection",
                "rate_limiting",
                "threat_detection",
                "security_monitoring",
                "backup_configured",
                "authentication",
            )
        }
        result = calculate_defense_score(checks)
        self.assertEqual(result["score"], 100)
        self.assertEqual(result["passed_controls"], 8)
    def test_missing_checks_do_not_pass(self):
        result = calculate_defense_score({})
        self.assertEqual(result["score"], 0)
        self.assertEqual(result["passed_controls"], 0)
        self.assertEqual(len(result["missing_controls"]), 8)
class TestAccessControl(unittest.TestCase):
    def test_unknown_ip_is_not_allowed_by_default(self):
        """
        The current access-control module is expected to deny an
        unlisted address under a default-deny policy.
        """
        result = evaluate_access(
            client_ip="203.0.113.10",
            port=443,
            policy={
                "default_policy": "deny",
                "allowed_ips": ["127.0.0.1"],
                "blocked_ips": [],
                "allowed_ports": [443],
            },
        )
        self.assertFalse(result.allowed)
class TestThreatDetector(unittest.TestCase):
    def test_suspicious_path_is_detected(self):
        detector = ThreatDetector()
        result = detector.inspect_path(
            client_id="test-client",
            path="/../../etc/passwd",
        )
        self.assertTrue(result)
if __name__ == "__main__":
    unittest.main(verbosity=2)