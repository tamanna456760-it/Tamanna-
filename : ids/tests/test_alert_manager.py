File: ids/tests/test_alert_manager.py

"""Tests for the Tamanna AI IDS alert manager."""
import unittest
from ids.alert_manager import AlertManager
class TestAlertManager(unittest.TestCase):
    def setUp(self):
        self.manager = AlertManager(
            max_alerts=3,
            minimum_severity="medium",
        )
    def make_alert(
        self,
        severity="medium",
        rule="test_rule",
        client_id="client-a",
        reason="Test alert",
    ):
        return {
            "severity": severity,
            "rule": rule,
            "client_id": client_id,
            "reason": reason,
            "timestamp": "2026-01-01T00:00:00Z",
        }
    def test_initial_count_is_zero(self):
        self.assertEqual(self.manager.count(), 0)
    def test_add_valid_medium_alert(self):
        result = self.manager.add_alert(self.make_alert())
        self.assertTrue(result)
        self.assertEqual(self.manager.count(), 1)
    def test_low_severity_alert_is_filtered(self):
        self.manager.add_alert(
            self.make_alert(severity="low")
        )
        self.assertEqual(self.manager.count(), 0)
    def test_high_severity_alert_is_retained(self):
        self.manager.add_alert(
            self.make_alert(severity="high")
        )
        alerts = self.manager.recent_alerts()
        self.assertEqual(len(alerts), 1)
        self.assertEqual(alerts[0]["severity"], "high")
    def test_invalid_severity_is_rejected(self):
        with self.assertRaises((TypeError, ValueError)):
            self.manager.add_alert(
                self.make_alert(severity="unknown")
            )
    def test_missing_required_fields_are_rejected(self):
        with self.assertRaises((TypeError, ValueError)):
            self.manager.add_alert({
                "severity": "high",
                "rule": "test_rule",
            })
    def test_alert_history_is_bounded(self):
        for number in range(5):
            self.manager.add_alert(
                self.make_alert(
                    severity="medium",
                    reason=f"Alert {number}",
                )
            )
        alerts = self.manager.recent_alerts()
        self.assertEqual(self.manager.count(), 3)
        self.assertEqual(len(alerts), 3)
        self.assertEqual(alerts[-1]["reason"], "Alert 4")
    def test_recent_alerts_can_filter_severity(self):
        self.manager.add_alert(
            self.make_alert(severity="medium")
        )
        self.manager.add_alert(
            self.make_alert(
                severity="critical",
                reason="Critical test",
            )
        )
        alerts = self.manager.recent_alerts(
            minimum_severity="critical"
        )
        self.assertEqual(len(alerts), 1)
        self.assertEqual(alerts[0]["severity"], "critical")
    def test_alerts_remain_monitor_only(self):
        self.manager.add_alert(
            self.make_alert(severity="high")
        )
        alert = self.manager.recent_alerts()[-1]
        self.assertEqual(alert["action"], "alert_only")
        self.assertFalse(alert["system_firewall_modified"])
    def test_summary_returns_dictionary(self):
        summary = self.manager.summary()
        self.assertIsInstance(summary, dict)
if __name__ == "__main__":
    unittest.main()