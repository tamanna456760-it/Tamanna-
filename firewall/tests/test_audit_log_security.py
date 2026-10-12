"""Security tests for Tamanna AI firewall audit logging."""
import json
import tempfile
import unittest
from pathlib import Path
from firewall.audit_log import AuditLogger
class TestAuditLogSecurity(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.log_path = Path(self.temp_dir.name) / "security_audit.jsonl"
        self.logger = AuditLogger(self.log_path)
    def tearDown(self):
        self.temp_dir.cleanup()
    def test_audit_log_file_is_created_after_event(self):
        self.logger.log_event(
            event_type="security_test",
            details={"source": "unit_test"},
        )
        self.assertTrue(self.log_path.exists())
    def test_each_log_line_is_valid_json(self):
        self.logger.log_event(
            event_type="login_failed",
            details={"client_id": "test-client"},
        )
        lines = self.log_path.read_text(encoding="utf-8").splitlines()
        self.assertGreater(len(lines), 0)
        for line in lines:
            with self.subTest(line=line):
                self.assertIsInstance(json.loads(line), dict)
    def test_log_verification_reports_valid_log(self):
        self.logger.log_event(
            event_type="policy_check",
            details={"allowed": False},
        )
        result = self.logger.verify_log()
        self.assertTrue(result)
if __name__ == "__main__":
    unittest.main()