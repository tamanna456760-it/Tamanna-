"""Tests for Tamanna AI WAF rule engine."""
import unittest
from waf.rule_engine import RuleEngine
def make_config():
    return {
        "project": "Tamanna AI",
        "mode": "monitor_only",
        "detection": {
            "sql_injection_detection": True,
            "cross_site_scripting_detection": True,
            "path_traversal_detection": True,
        },
        "rules": {
            "inspect_query_string": True,
            "inspect_path": True,
            "inspect_headers": True,
            "inspect_request_body": True,
            "maximum_body_inspection_bytes": 65536,
        },
    }
class TestRuleEngine(unittest.TestCase):
    def setUp(self):
        self.engine = RuleEngine(make_config())
    def test_normal_request_has_no_findings(self):
        result = self.engine.inspect(
            path="/products",
            query_string="page=1",
            headers={"accept": "application/json"},
            body="",
        )
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["finding_count"], 0)
    def test_sql_injection_pattern_is_detected(self):
        result = self.engine.inspect(
            query_string="id=1%20UNION%20SELECT%20name%20FROM%20users"
        )
        self.assertIn(
            "sql_injection",
            [item["rule"] for item in result["findings"]],
        )
    def test_xss_pattern_is_detected(self):
        result = self.engine.inspect(
            query_string="q=<script>alert(1)</script>"
        )
        self.assertIn(
            "cross_site_scripting",
            [item["rule"] for item in result["findings"]],
        )
    def test_path_traversal_is_detected(self):
        result = self.engine.inspect(
            path="/files/../../etc/passwd"
        )
        self.assertIn(
            "path_traversal",
            [item["rule"] for item in result["findings"]],
        )
    def test_sql_detection_can_be_disabled(self):
        config = make_config()
        config["detection"]["sql_injection_detection"] = False
        engine = RuleEngine(config)
        result = engine.inspect(
            query_string="id=1 UNION SELECT name FROM users"
        )
        self.assertNotIn(
            "sql_injection",
            [item["rule"] for item in result["findings"]],
        )
    def test_request_is_never_blocked(self):
        result = self.engine.inspect(
            query_string="q=<script>alert(1)</script>"
        )
        self.assertFalse(result["request_blocked"])
        self.assertFalse(result["system_firewall_modified"])
if __name__ == "__main__":
    unittest.main()