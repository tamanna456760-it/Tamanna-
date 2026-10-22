"""Tests for Tamanna AI WAF health checks."""
import json
import tempfile
import unittest
from pathlib import Path
from waf.health_check import run_health_check
def make_config():
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
            "file": "data/waf_events.jsonl",
            "redact_secrets": True,
            "max_event_size_bytes": 16384,
        },
        "alerts": {
            "enabled": True,
            "minimum_severity": "medium",
        },
        "enforcement": {
            "block_requests": False,
            "modify_system_firewall": False,
            "require_manual_approval": True,
        },
    }
class TestWAFHealthCheck(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.config_path = Path(self.temp_dir.name) / "waf_config.json"
    def tearDown(self):
        self.temp_dir.cleanup()
    def write_config(self, config):
        self.config_path.write_text(
            json.dumps(config),
            encoding="utf-8",
        )
    def test_valid_config_is_healthy(self):
        self.write_config(make_config())
        result = run_health_check(str(self.config_path))
        self.assertEqual(result["status"], "healthy")
        self.assertEqual(result["checks"]["config_load"], "ok")
        self.assertEqual(result["checks"]["safety_config"], "ok")
        self.assertFalse(result["request_blocking"])
        self.assertFalse(result["system_firewall_modification"])
    def test_missing_config_is_unhealthy(self):
        result = run_health_check(
            str(Path(self.temp_dir.name) / "missing.json")
        )
        self.assertEqual(result["status"], "unhealthy")
    def test_wrong_project_is_unhealthy(self):
        config = make_config()
        config["project"] = "Unknown Project"
        self.write_config(config)
        result = run_health_check(str(self.config_path))
        self.assertEqual(result["status"], "unhealthy")
    def test_non_monitor_only_mode_is_unhealthy(self):
        config = make_config()
        config["mode"] = "blocking"
        self.write_config(config)
        result = run_health_check(str(self.config_path))
        self.assertEqual(result["status"], "unhealthy")
    def test_request_blocking_must_remain_disabled(self):
        config = make_config()
        config["enforcement"]["block_requests"] = True
        self.write_config(config)
        result = run_health_check(str(self.config_path))
        self.assertEqual(result["status"], "unhealthy")
    def test_invalid_json_is_unhealthy(self):
        self.config_path.write_text(
            "{ invalid json",
            encoding="utf-8",
        )
        result = run_health_check(str(self.config_path))
        self.assertEqual(result["status"], "unhealthy")
if __name__ == "__main__":
    unittest.main()