"""Integration tests for Tamanna AI IDS."""
import unittest
from ids.ids_manager import IDSManager
class TestIDSIntegration(unittest.TestCase):
    """Test the IDS components working together."""
    def setUp(self):
        self.manager = IDSManager(
            enabled=True,
            mode="monitor_only",
            failed_login_threshold=3,
            failed_login_window=300,
            request_rate_threshold=4,
            request_rate_window=60,
        )
    def test_failed_logins_generate_alert(self):
        """Repeated failed logins should generate a detection alert."""
        for _ in range(3):
            self.manager.record_failed_login(
                client_id="test-client",
                now=1000,
            )
        alerts = self.manager.recent_alerts()
        self.assertTrue(
            any(
                "login" in str(alert).lower()
                or "failed" in str(alert).lower()
                for alert in alerts
            ),
            "Expected an alert after repeated failed logins.",
        )
    def test_events_are_collected(self):
        """Valid events should be accepted by the manager."""
        result = self.manager.record_event(
            {
                "event_type": "integration_test",
                "message": "Tamanna AI IDS integration test",
            }
        )
        self.assertTrue(result)
        events = self.manager.recent_events()
        self.assertTrue(events)
    def test_monitor_only_mode_is_preserved(self):
        """Detection must not modify the system firewall."""
        for _ in range(3):
            self.manager.record_failed_login(
                client_id="safety-test-client",
                now=2000,
            )
        summary = self.manager.summary()
        self.assertEqual(self.manager.mode, "monitor_only")
        self.assertFalse(
            summary.get("system_firewall_modified", False)
        )
    def test_request_detection_does_not_block_client(self):
        """High request volume must not trigger automatic blocking."""
        for _ in range(5):
            self.manager.record_request(
                client_id="request-test-client",
                path="/",
                now=3000,
            )
        alerts = self.manager.recent_alerts()
        for alert in alerts:
            self.assertNotEqual(
                alert.get("action"),
                "block",
            )
            self.assertFalse(
                alert.get("system_firewall_modified", False)
            )
if __name__ == "__main__":
    unittest.main()