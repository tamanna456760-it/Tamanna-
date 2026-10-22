File: ids/tests/test_ids_manager.py

"""Tests for the Tamanna AI IDS manager."""
import unittest
from ids.ids_manager import IDSManager
class TestIDSManager(unittest.TestCase):
    def setUp(self):
        self.ids = IDSManager(
            enabled=True,
            mode="monitor_only",
            max_events=20,
            max_alerts=20,
            minimum_severity="low",
            failed_login_threshold=3,
            failed_login_window=300,
            request_rate_threshold=3,
            request_rate_window=60,
        )
    def test_manager_starts_in_monitor_only_mode(self):
        status = self.ids.summary()
        self.assertTrue(status["enabled"])
        self.assertEqual(status["mode"], "monitor_only")
        self.assertFalse(status["automatic_ip_blocking"])
        self.assertFalse(status["system_firewall_modified"])
    def test_general_event_is_recorded(self):
        result = self.ids.record_event({
            "type": "test_event",
            "message": "IDS manager test",
        })
        self.assertTrue(result)
        self.assertEqual(len(self.ids.recent_events()), 1)
    def test_invalid_general_event_is_rejected(self):
        with self.assertRaises((TypeError, ValueError)):
            self.ids.record_event("invalid")
    def test_failed_logins_generate_an_alert(self):
        self.ids.record_failed_login("client-a", now=1000)
        self.ids.record_failed_login("client-a", now=1001)
        alert = self.ids.record_failed_login(
            "client-a", now=1002
        )
        self.assertIsNotNone(alert)
        self.assertEqual(alert["action"], "alert_only")
        self.assertFalse(alert["system_firewall_modified"])
    def test_normal_requests_are_collected(self):
        self.ids.record_request(
            "client-a", "/home", now=1000
        )
        self.ids.record_request(
            "client-a", "/about", now=1001
        )
        events = self.ids.recent_events()
        self.assertEqual(len(events), 2)
        self.assertEqual(events[0]["type"], "request")
    def test_suspicious_request_generates_an_alert(self):
        alert = self.ids.record_request(
            "client-a", "/.env", now=1000
        )
        self.assertIsNotNone(alert)
        self.assertEqual(alert["action"], "alert_only")
    def test_disabled_manager_does_not_record_events(self):
        disabled_ids = IDSManager(enabled=False)
        result = disabled_ids.record_event({
            "type": "ignored_event",
        })
        self.assertFalse(result)
        self.assertEqual(len(disabled_ids.recent_events()), 0)
    def test_disabled_manager_does_not_process_failed_logins(self):
        disabled_ids = IDSManager(enabled=False)
        alert = disabled_ids.record_failed_login(
            "client-a", now=1000
        )
        self.assertIsNone(alert)
        self.assertEqual(len(disabled_ids.recent_events()), 0)
    def test_health_contains_component_status(self):
        result = self.ids.health()
        self.assertIn("collector", result)
        self.assertIn("detector", result)
        self.assertIn("alerts", result)
    def test_unsupported_mode_is_rejected(self):
        with self.assertRaises(ValueError):
            IDSManager(mode="automatic_blocking")
    def test_summary_counts_recorded_events(self):
        self.ids.record_event({"type": "one"})
        self.ids.record_event({"type": "two"})
        summary = self.ids.summary()
        self.assertEqual(summary["event_count"], 2)
if __name__ == "__main__":
    unittest.main()