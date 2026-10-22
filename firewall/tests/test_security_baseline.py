"""
Tamanna AI Firewall - Security Baseline Tests
Owner: HM INSAN ALI
"""
import unittest
from firewall.security_baseline import check_security_baseline
def safe_config():
    return {
        "mode": "audit_only",
        "default_policy": "deny",
        "allowed_ips": ["127.0.0.1", "::1"],
        "allowed_ports": [],
        "system_firewall": {
            "modify_system_rules": False,
        },
    }
class TestSecurityBaseline(unittest.TestCase):
    def test_safe_configuration_passes(self):
        report = check_security_baseline(safe_config())
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(report["checks_passed"], report["checks_total"])
        self.assertFalse(report["system_rules_modified"])
    def test_enforce_mode_requires_review(self):
        config = safe_config()
        config["mode"] = "enforce"
        report = check_security_baseline(config)
        self.assertEqual(report["status"], "REVIEW_REQUIRED")
        self.assertFalse(report["checks"]["audit_only_mode"])
    def test_allow_by_default_requires_review(self):
        config = safe_config()
        config["default_policy"] = "allow"
        report = check_security_baseline(config)
        self.assertEqual(report["status"], "REVIEW_REQUIRED")
        self.assertFalse(report["checks"]["default_deny"])
    def test_system_rule_modification_must_be_disabled(self):
        config = safe_config()
        config["system_firewall"]["modify_system_rules"] = True
        report = check_security_baseline(config)
        self.assertEqual(report["status"], "REVIEW_REQUIRED")
        self.assertFalse(
            report["checks"]["system_rule_changes_disabled"]
        )
    def test_invalid_ip_list_type_requires_review(self):
        config = safe_config()
        config["allowed_ips"] = "127.0.0.1"
        report = check_security_baseline(config)
        self.assertEqual(report["status"], "REVIEW_REQUIRED")
        self.assertFalse(report["checks"]["allowed_ips_is_list"])
    def test_invalid_port_list_type_requires_review(self):
        config = safe_config()
        config["allowed_ports"] = "8000"
        report = check_security_baseline(config)
        self.assertEqual(report["status"], "REVIEW_REQUIRED")
        self.assertFalse(report["checks"]["allowed_ports_is_list"])
    def test_non_dictionary_input_is_rejected(self):
        with self.assertRaises(TypeError):
            check_security_baseline([])
if __name__ == "__main__":
    unittest.main(verbosity=2)