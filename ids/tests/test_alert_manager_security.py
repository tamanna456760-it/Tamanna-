"""Security tests for the IDS alert manager."""
import unittest
from ids.alert_manager import AlertManager
class TestAlertManagerSecurity(unittest.TestCase):
    def setUp(self):
        self.manager = AlertManager(
            max_alerts=2,
            minimum_severity="medium",
        )
    def make_alert(self, severity="high"):
        return {
            "rule": "repeated_failed_login",
            "severity": severity,
            "reason": "Repeated failed login attempts",
            "client_id": "test-client",
            "action": "alert_only",
            "system_firewall_modified": False,
        }
    def test_alert_does_not_request_firewall_changes(self):
        self.manager.add_alert(self.make_alert())
        alerts = self.manager.recent_alerts()
        self.assertTrue(alerts)
        for alert in alerts:
            self.assertEqual(alert.get("action"), "alert_only")
            self.assertFalse(
                alert.get("system_firewall_modified", False)
            )
    def test_low_severity_alert_is_filtered(self):
        self.manager.add_alert(self.make_alert(severity="low"))
        self.assertEqual(self.manager.count(), 0)
    def test_alert_storage_is_bounded(self):
        for number in range(5):
            alert = self.make_alert()
            alert["reason"] = f"Test alert {number}"
            self.manager.add_alert(alert)
        self.assertLessEqual(self.manager.count(), 2)
if __name__ == "__main__":
    unittest.main()