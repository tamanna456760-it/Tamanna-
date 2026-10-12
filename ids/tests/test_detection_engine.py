File: ids/tests/test_detection_engine.py

"""Tests for the Tamanna AI IDS detection engine."""
import unittest
from ids.detection_engine import DetectionEngine
class TestDetectionEngine(unittest.TestCase):
    def setUp(self):
        self.engine = DetectionEngine(
            failed_login_threshold=3,
            failed_login_window=300,
            request_rate_threshold=3,
            request_rate_window=60,
        )
    def test_initial_health(self):
        result = self.engine.health()
        self.assertIsInstance(result, dict)
    def test_failed_login_below_threshold(self):
        first = self.engine.record_failed_login(
            "client-a", now=1000
        )
        second = self.engine.record_failed_login(
            "client-a", now=1001
        )
        self.assertIsNone(first)
        self.assertIsNone(second)
    def test_failed_login_threshold_triggers_alert(self):
        self.engine.record_failed_login("client-a", now=1000)
        self.engine.record_failed_login("client-a", now=1001)
        alert = self.engine.record_failed_login(
            "client-a", now=1002
        )
        self.assertIsNotNone(alert)
        self.assertIn("severity", alert)
        self.assertIn("rule", alert)
    def test_failed_logins_are_tracked_per_client(self):
        self.engine.record_failed_login("client-a", now=1000)
        self.engine.record_failed_login("client-a", now=1001)
        alert = self.engine.record_failed_login(
            "client-b", now=1002
        )
        self.assertIsNone(alert)
    def test_normal_requests_below_threshold(self):
        self.assertIsNone(
            self.engine.record_request(
                "client-a", path="/home", now=1000
            )
        )
        self.assertIsNone(
            self.engine.record_request(
                "client-a", path="/about", now=1001
            )
        )
    def test_request_rate_threshold_triggers_alert(self):
        for timestamp in (1000, 1001, 1002):
            self.engine.record_request(
                "client-a", path="/home", now=timestamp
            )
        alert = self.engine.record_request(
            "client-a", path="/home", now=1003
        )
        self.assertIsNotNone(alert)
        self.assertIn("rule", alert)
    def test_suspicious_path_triggers_alert(self):
        alert = self.engine.record_request(
            "client-a", path="/.env", now=1000
        )
        self.assertIsNotNone(alert)
    def test_alerts_are_monitor_only(self):
        alert = self.engine.record_failed_login(
            "client-a", now=1000
        )
        alert = self.engine.record_failed_login(
            "client-a", now=1001
        )
        alert = self.engine.record_failed_login(
            "client-a", now=1002
        )
        self.assertEqual(alert["action"], "alert_only")
        self.assertFalse(alert["system_firewall_modified"])
    def test_separate_clients_have_separate_request_windows(self):
        for timestamp in (1000, 1001, 1002):
            self.engine.record_request(
                "client-a", path="/home", now=timestamp
            )
        alert = self.engine.record_request(
            "client-b", path="/home", now=1003
        )
        self.assertIsNone(alert)
if __name__ == "__main__":
    unittest.main()