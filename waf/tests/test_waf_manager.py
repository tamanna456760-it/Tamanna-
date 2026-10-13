"""Tests for Tamanna AI WAF manager."""
import tempfile
import os
import unittest
from waf.waf_manager import WAFManager
def make_config(log_path):
    return {
        "project": "Tamanna AI",
        "owner": "HM INSAN ALI",
        "enabled": True,
        "mode": "monitor_only",
        "request_limits": {
            "max_request_size_bytes": 1048576,
            "max_url_length": 8192,
            "max_header_count": 100,
            "max_header_value_length": 8192,
            "max_query_parameters": 200,
        },
        "detection": {
            "sql_injection_detection": True,
            "cross_site_scripting_detection": True,
            "path_traversal_detection": True,
            "malformed_request_detection": True,
            "suspicious_user_agent_detection": True,
            "oversized_request_detection": True,
        },
        "rules": {
            "inspect_query_string": True,
            "inspect_path": True,
            "inspect_headers": True,
            "inspect_request_body": True,
            "maximum_body_inspection_bytes": 65536,
        },
        "logging": {
            "enabled": True,
            "file": log_path,
            "redact_secrets": True,
            "max_event_size_bytes": 16384,
        },
        "enforcement": {
            "block_requests": False,
            "modify_system_firewall": False,
            "require_manual_approval": True,
        },
    }
class TestWAFManager(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        log_path = os.path.join(
            self.temp_dir.name, "waf_events.jsonl"
        )
        self.manager = WAFManager(make_config(log_path))
    def tearDown(self):
        self.temp_dir.cleanup()
    def test_normal_request_is_ok(self):
        result = self.manager.inspect_request(
            path="/products",
            query_string="page=1",
            headers={"accept": "application/json"},
            body=b"",
        )
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["finding_count"], 0)
    def test_suspicious_request_generates_findings(self):
        result = self.manager.inspect_request(
            path="/search",
            query_string="q=<script>alert(1)</script>",
        )
        self.assertEqual(result["status"], "alert")
        self.assertGreater(result["finding_count"], 0)
    def test_manager_never_blocks_requests(self):
        result = self.manager.inspect_request(
            path="/files/../../etc/passwd"
        )
        self.assertFalse(result["request_blocked"])
        self.assertFalse(result["system_firewall_modified"])
    def test_health_reports_monitor_only_mode(self):
        result = self.manager.health()
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["mode"], "monitor_only")
        self.assertFalse(result["request_blocking"])
        self.assertFalse(result["system_firewall_modification"])
    def test_unsupported_mode_is_rejected(self):
        config = make_config(os.path.join(
            self.temp_dir.name, "other.jsonl"
        ))
        config["mode"] = "blocking"
        with self.assertRaises(ValueError):
            WAFManager(config)
    def test_request_blocking_configuration_is_rejected(self):
        config = make_config(os.path.join(
            self.temp_dir.name, "blocked.jsonl"
        ))
        config["enforcement"]["block_requests"] = True
        with self.assertRaises(ValueError):
            WAFManager(config)
if __name__ == "__main__":
    unittest.main()