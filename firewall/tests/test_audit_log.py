"""
Tamanna AI — Audit Log Tests
Owner: HM INSAN ALI
Run from the repository root:
    python -m unittest firewall.tests.test_audit_log -v
Tests use temporary local files only.
"""
import json
import tempfile
import unittest
from pathlib import Path
from firewall.audit_log import AuditLogger
class TestAuditLogger(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.log_path = Path(self.temp_dir.name) / "audit.jsonl"
        self.logger = AuditLogger(self.log_path)
    def tearDown(self):
        self.temp_dir.cleanup()
    def test_event_is_written(self):
        self.logger.log_event(
            event_type="test_event",
            details={"result": "passed"},
        )
        self.assertTrue(self.log_path.exists())
        lines = self.log_path.read_text(
            encoding="utf-8"
        ).splitlines()
        self.assertEqual(len(lines), 1)
        event = json.loads(lines[0])
        self.assertEqual(event["event_type"], "test_event")
    def test_sensitive_values_are_not_logged(self):
        self.logger.log_event(
            event_type="authentication_test",
            details={
                "password": "do-not-store-this",
                "result": "failed",
            },
        )
        contents = self.log_path.read_text(encoding="utf-8")
        self.assertNotIn("do-not-store-this", contents)
        self.assertIn("failed", contents)
    def test_log_integrity_verification(self):
        self.logger.log_event(
            event_type="first",
            details={"sequence": 1},
        )
        self.logger.log_event(
            event_type="second",
            details={"sequence": 2},
        )
        verification = self.logger.verify_log()
        # Accommodate implementations that return either a boolean
        # or a dictionary containing a validity field.
        if isinstance(verification, dict):
            valid = verification.get(
                "valid",
                verification.get("ok", False),
            )
        else:
            valid = verification
        self.assertTrue(valid)
    def test_modified_log_is_detected(self):
        self.logger.log_event(
            event_type="integrity_test",
            details={"message": "original"},
        )
        lines = self.log_path.read_text(
            encoding="utf-8"
        ).splitlines()
        event = json.loads(lines[0])
        event["details"]["message"] = "tampered"
        self.log_path.write_text(
            json.dumps(event) + "\n",
            encoding="utf-8",
        )
        verification = self.logger.verify_log()
        if isinstance(verification, dict):
            valid = verification.get(
                "valid",
                verification.get("ok", False),
            )
        else:
            valid = verification
        self.assertFalse(valid)
if __name__ == "__main__":
    unittest.main(verbosity=2)