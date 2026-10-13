"""Security tests for the IDS event collector."""
import unittest
from ids.event_collector import EventCollector
class TestEventCollectorSecurity(unittest.TestCase):
    def setUp(self):
        self.collector = EventCollector(
            max_events=3,
            max_event_size=256,
        )
    def test_sensitive_dictionary_fields_are_redacted(self):
        self.collector.add_event({
            "event_type": "authentication",
            "password": "example-secret",
            "api_token": "example-token",
            "details": {
                "access_token": "nested-secret",
            },
        })
        events = self.collector.recent()
        self.assertTrue(events)
        serialized = str(events)
        self.assertNotIn("example-secret", serialized)
        self.assertNotIn("example-token", serialized)
        self.assertNotIn("nested-secret", serialized)
    def test_event_count_is_bounded(self):
        for number in range(5):
            self.collector.add_event({
                "event_type": "test",
                "number": number,
            })
        self.assertLessEqual(self.collector.count(), 3)
    def test_non_dictionary_event_is_rejected(self):
        with self.assertRaises((TypeError, ValueError)):
            self.collector.add_event("not-a-dictionary")
    def test_sensitive_values_inside_free_text_are_not_assumed_safe(self):
        # This test documents the current limitation: redaction of secrets
        # embedded inside arbitrary text strings is not guaranteed.
        self.collector.add_event({
            "event_type": "test",
            "message": "Authorization: Bearer example-secret",
        })
        events = self.collector.recent()
        self.assertTrue(events)
if __name__ == "__main__":
    unittest.main()