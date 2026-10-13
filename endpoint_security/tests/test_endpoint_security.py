"""Unit tests for Tamanna AI Endpoint Security.
Owner: HM INSAN ALI
"""
import hashlib
import tempfile
import unittest
from pathlib import Path
from endpoint_security.file_integrity import FileIntegrityMonitor
from endpoint_security.manager import EndpointSecurityManager
def make_config():
    return {
        "project": "Tamanna AI",
        "owner": "HM INSAN ALI",
        "enabled": True,
        "mode": "monitor_only",
        "monitoring": {
            "process_monitoring": False,
            "file_integrity_monitoring": True,
        },
        "process_monitoring": {
            "alert_on_unknown_executables": False,
            "allowlist": [],
        },
        "file_integrity": {
            "enabled": True,
            "hash_algorithm": "sha256",
            "follow_symlinks": False,
            "max_file_size_bytes": 1024 * 1024,
        },
        "logging": {
            "enabled": False,
            "file": "data/test_endpoint_events.jsonl",
            "redact_secrets": True,
            "max_event_size_bytes": 16384,
        },
        "enforcement": {
            "kill_processes": False,
            "quarantine_files": False,
            "delete_files": False,
            "modify_system_settings": False,
            "require_manual_approval": True,
        },
    }
class TestEndpointSecurity(unittest.TestCase):
    def test_manager_health_is_monitor_only(self):
        manager = EndpointSecurityManager(make_config())
        result = manager.health()
        self.assertEqual(result["status"], "healthy")
        self.assertEqual(result["mode"], "monitor_only")
        self.assertFalse(result["enforcement_enabled"])
    def test_rejects_process_termination_configuration(self):
        config = make_config()
        config["enforcement"]["kill_processes"] = True
        with self.assertRaises(ValueError):
            EndpointSecurityManager(config)
    def test_hash_file(self):
        with tempfile.TemporaryDirectory() as directory:
            file_path = Path(directory) / "sample.txt"
            file_path.write_text("Tamanna AI", encoding="utf-8")
            monitor = FileIntegrityMonitor(make_config())
            result = monitor.hash_file(file_path)
            expected = hashlib.sha256(b"Tamanna AI").hexdigest()
            self.assertEqual(result["status"], "ok")
            self.assertEqual(result["sha256"], expected)
    def test_compare_unchanged_file(self):
        with tempfile.TemporaryDirectory() as directory:
            file_path = Path(directory) / "sample.txt"
            file_path.write_text("unchanged", encoding="utf-8")
            baseline = hashlib.sha256(b"unchanged").hexdigest()
            monitor = FileIntegrityMonitor(make_config())
            result = monitor.compare(file_path, baseline)
            self.assertEqual(result["status"], "unchanged")
    def test_compare_changed_file(self):
        with tempfile.TemporaryDirectory() as directory:
            file_path = Path(directory) / "sample.txt"
            file_path.write_text("modified", encoding="utf-8")
            baseline = hashlib.sha256(b"original").hexdigest()
            monitor = FileIntegrityMonitor(make_config())
            result = monitor.compare(file_path, baseline)
            self.assertEqual(result["status"], "changed")
    def test_rejects_invalid_baseline(self):
        monitor = FileIntegrityMonitor(make_config())
        result = monitor.compare("missing.txt", "not-a-hash")
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["reason"], "invalid SHA-256 baseline")
if __name__ == "__main__":
    unittest.main()