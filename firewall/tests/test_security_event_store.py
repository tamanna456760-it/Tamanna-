"""
Tamanna AI Firewall - Security Event Store Tests
Owner: HM INSAN ALI
"""
import json
import tempfile
import unittest
from pathlib import Path
from firewall.security_event_store import SecurityEventStore
class TestSecurityEventStore(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.log_path = Path(self.temp_dir.name) / "events.jsonl"
        self.store = SecurityEventStore(self.log_path)
    def test_append_event_creates_jsonl_file(self):
        event = self.store.append_event(
            event_type="login_failed",
            severity="MEDIUM",
            details={"client": "test-client"},
        )
        self.assertTrue(self.log_path.is_file())
        self.assertEqual(event["event_type"], "login_failed")
        self.assertEqual(event["severity"], "MEDIUM")
    def test_saved_event_is_valid_json(self):
        self.store.append_event(
            event_type="request_received",
            details={"path": "/health"},
        )
        lines = self.log_path.read_text(
            encoding="utf-8"
        ).splitlines()
        self.assertEqual(len(lines), 1)
        saved = json.loads(lines[0])
        self.assertEqual(saved["event_type"], "request_received")
    def test_secret_fields_are_redacted(self):
        event = self.store.append_event(
            event_type="authentication_attempt",
            details={
                "api_key": "do-not-store-this",
                "nested": {"access_token": "secret-value"},
            },
        )
        self.assertEqual(event["details"]["api_key"], "[REDACTED]")
        self.assertEqual(
            event["details"]["nested"]["access_token"],
            "[REDACTED]",
        )
        saved_text = self.log_path.read_text(encoding="utf-8")
        self.assertNotIn("do-not-store-this", saved_text)
        self.assertNotIn("secret-value", saved_text)
    def test_read_events_returns_saved_events(self):
        self.store.append_event("event_one")
        self.store.append_event("event_two", severity="LOW")
        events = self.store.read_events(limit=10)
        self.assertEqual(len(events), 2)
        self.assertEqual(events[0]["event_type"], "event_one")
        self.assertEqual(events[1]["event_type"], "event_two")
    def test_read_events_respects_limit(self):
        for number in range(5):
            self.store.append_event(f"event_{number}")
        events = self.store.read_events(limit=2)
        self.assertEqual(len(events), 2)
        self.assertEqual(events[0]["event_type"], "event_3")
        self.assertEqual(events[1]["event_type"], "event_4")
    def test_missing_log_returns_empty_list(self):
        self.assertEqual(self.store.read_events(), [])
    def test_empty_event_type_is_rejected(self):
        with self.assertRaises(ValueError):
            self.store.append_event("")
    def test_unsupported_severity_is_rejected(self):
        with self.assertRaises(ValueError):
            self.store.append_event(
                event_type="test",
                severity="UNKNOWN",
            )
    def test_non_dictionary_details_are_rejected(self):
        with self.assertRaises(TypeError):
            self.store.append_event(
                event_type="test",
                details=["unexpected"],
            )
    def test_oversized_event_is_rejected(self):
        with self.assertRaises(ValueError):
            self.store.append_event(
                event_type="large_event",
                details={"payload": "x" * 20_000},
            )
    def test_invalid_json_lines_are_skipped(self):
        self.store.append_event("valid_event")
        with self.log_path.open("a", encoding="utf-8") as file:
            file.write("{invalid-json\n")
        events = self.store.read_events()
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["event_type"], "valid_event")
if __name__ == "__main__":
    unittest.main(verbosity=2)