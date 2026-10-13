"""Tests for URL normalization in Tamanna AI WAF.
Owner: HM INSAN ALI
These tests define expected detection behavior for encoded inputs.
They may fail until normalization is implemented in rule_engine.py.
"""
import unittest
from waf.rule_engine import RuleEngine
class TestEncodedAttackDetection(unittest.TestCase):
    def setUp(self):
        self.engine = RuleEngine({
            "enabled": True,
            "rules": {
                "inspect_query_string": True,
                "inspect_path": True,
                "inspect_headers": True,
                "inspect_request_body": True,
                "case_insensitive_matching": True,
            },
            "detection": {
                "sql_injection_detection": True,
                "cross_site_scripting_detection": True,
                "path_traversal_detection": True,
                "malformed_request_detection": True,
                "suspicious_user_agent_detection": True,
                "oversized_request_detection": True,
            },
        })
    def test_encoded_sql_injection(self):
        result = self.engine.inspect(
            path="/search",
            query_string="id=1%20UNION%20SELECT%20name%20FROM%20users",
        )
        self.assertTrue(
            result["findings"],
            "Expected encoded SQL injection pattern to be detected",
        )
    def test_encoded_path_traversal(self):
        result = self.engine.inspect(
            path="/files/%2e%2e/%2e%2e/etc/passwd",
        )
        self.assertTrue(
            result["findings"],
            "Expected encoded path traversal to be detected",
        )
    def test_normal_encoded_text_is_not_always_blocked(self):
        result = self.engine.inspect(
            path="/search",
            query_string="q=hello%20world",
        )
        self.assertFalse(result["request_blocked"])
if __name__ == "__main__":
    unittest.main()