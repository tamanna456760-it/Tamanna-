File: ids/tests/test_event_collector.py

"""Tests for the Tamanna AI IDS event collector."""
import json
import unittest
from ids.event_collector import EventCollector
class TestEventCollector(unittest.TestCase):
    def setUp(self):
        self.collector = EventCollector(
            max_events=3,
            max_event_size=16384,
        )
    def test_initial_count_is_zero(self):
        self.assertEqual(self.collector.count(), 0)
    def test_add_valid_event(self):
        result = self.collector.add_event({
            "type": "login",
            "status": "success",
        })
        self.assertTrue(result)
        self.assertEqual(self.collector.count(), 1)
    def test_recent_returns_added_event(self):
        self.collector.add_event({
            "type": "request",
            "path": "/home",
        })
        events = self.collector.recent()
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["type"], "request")
        self.assertEqual(events[0]["path"], "/home")
    def test_event_history_is_bounded(self):
        for number in range(5):
            self.collector.add_event({
                "type": "test",
                "number": number,
            })
        events = self.collector.recent()
        self.assertEqual(self.collector.count(), 3)
        self.assertEqual(len(events), 3)
        self.assertEqual(events[-1]["number"], 4)
    def test_non_dictionary_event_is_rejected(self):
        with self.assertRaises((TypeError, ValueError)):
            self.collector.add_event("invalid event")
    def test_secret_fields_are_redacted(self):
        self.collector.add_event({
            "type": "authentication",
            "password": "example-password",
            "api_key": "example-api-key",
            "details": {
                "access_token": "example-token",
            },
        })
        event = self.collector.recent()[-1]
        serialized = json.dumps(event).lower()
        self.assertNotIn("example-password", serialized)
        self.assertNotIn("example-api-key", serialized)
        self.assertNotIn("example-token", serialized)
    def test_event_has_timestamp(self):
        self.collector.add_event({"type": "health_check"})
        event = self.collector.recent()[-1]
        self.assertIn("timestamp", event)
        self.assertTrue(event["timestamp"])
    def test_health_returns_status_information(self):
        result = self.collector.health()
        self.assertIsInstance(result, dict)
    def test_inspect_suspicious_path(self):
        result = self.collector.inspect_path("/.env")
        self.assertTrue(result)
    def test_inspect_normal_path(self):
        result = self.collector.inspect_path("/home")
        self.assertFalse(result)
if __name__ == "__main__":
    unittest.main()