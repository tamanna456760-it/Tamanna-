"""Tests for Tamanna AI WAF request inspector."""
import unittest
from waf.request_inspector import RequestInspector
def make_config():
    return {
        "project": "Tamanna AI",
        "mode": "monitor_only",
        "request_limits": {
            "max_request_size_bytes": 32,
            "max_url_length": 12,
            "max_header_count": 2,
            "max_header_value_length": 16,
            "max_query_parameters": 2,
        },
    }
class TestRequestInspector(unittest.TestCase):
    def setUp(self):
        self.inspector = RequestInspector(make_config())
    def test_normal_request_has_no_findings(self):
        result = self.inspector.inspect(
            path="/home",
            headers={"accept": "application/json"},
            query_parameters={"page": "1"},
            body=b"hello",
        )
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["finding_count"], 0)
        self.assertFalse(result["request_blocked"])
    def test_long_url_is_detected(self):
        result = self.inspector.inspect(path="/" + "a" * 20)
        self.assertIn(
            "url_too_long",
            [item["rule"] for item in result["findings"]],
        )
    def test_too_many_headers_are_detected(self):
        result = self.inspector.inspect(
            headers={
                "accept": "text/plain",
                "user-agent": "test",
                "x-extra": "value",
            }
        )
        self.assertIn(
            "too_many_headers",
            [item["rule"] for item in result["findings"]],
        )
    def test_oversized_body_is_detected(self):
        result = self.inspector.inspect(body=b"x" * 40)
        self.assertIn(
            "request_body_too_large",
            [item["rule"] for item in result["findings"]],
        )
    def test_too_many_query_parameters_are_detected(self):
        result = self.inspector.inspect(
            query_parameters={
                "a": "1",
                "b": "2",
                "c": "3",
            }
        )
        self.assertIn(
            "too_many_query_parameters",
            [item["rule"] for item in result["findings"]],
        )
    def test_request_is_never_blocked(self):
        result = self.inspector.inspect(path="/" + "z" * 50)
        self.assertFalse(result["request_blocked"])
        self.assertFalse(result["system_firewall_modified"])
if __name__ == "__main__":
    unittest.main()