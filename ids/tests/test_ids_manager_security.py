"""Security tests for Tamanna AI IDS Manager."""
import unittest
from ids.ids_manager import IDSManager
class TestIDSManagerSecurity(unittest.TestCase):
    def setUp(self):
        self.manager = IDSManager(
            enabled=True,
            mode="monitor_only",
            failed_login_threshold=3,
            failed_login_window=300,
            request_rate_threshold=4,
            request_rate_window=60,
        )
    def test_manager_stays_in_monitor_only_mode(self):
        self.assertEqual(self.manager.mode, "monitor_only")
    def test_collected_event_does_not_expose_input_secret(self):
        self.manager.record_event({
            "event_type": "security_test",
            "password": "test-password-should-be-redacted",
        })
        events = self.manager.recent_events()
        self.assertNotIn(
            "test-password-should-be-redacted",
            str(events),
        )
    def test_failed_login_alerts_never_block(self):
        for _ in range(3):
            self.manager.record_failed_login(
                client_id="manager-security-test",
                now=1000,
            )
        for alert in self.manager.recent_alerts():
            self.assertEqual(alert.get("action"), "alert_only")
            self.assertFalse(
                alert.get("system_firewall_modified", False)
            )
    def test_request_alerts_never_modify_firewall(self):
        for timestamp in range(1000, 1006):
            self.manager.record_request(
                client_id="manager-rate-test",
                path="/",
                now=timestamp,
            )
        for alert in self.manager.recent_alerts():
            self.assertNotEqual(alert.get("action"), "block")
            self.assertFalse(
                alert.get("system_firewall_modified", False)
            )
    def test_health_returns_a_dictionary(self):
        health = self.manager.health()
        self.assertIsInstance(health, dict)
if __name__ == "__main__":
    unittest.main()