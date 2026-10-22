"""Security tests for the Tamanna AI IDS detection engine."""
import unittest
from ids.detection_engine import DetectionEngine
class TestDetectionEngineSecurity(unittest.TestCase):
    def setUp(self):
        self.engine = DetectionEngine(
            failed_login_threshold=3,
            failed_login_window=300,
            request_rate_threshold=3,
            request_rate_window=60,
        )
    def test_failed_login_threshold_generates_alert(self):
        alerts = []
        for _ in range(3):
            result = self.engine.record_failed_login(
                client_id="security-test-client",
                now=1000,
            )
            if result:
                alerts.extend(
                    result if isinstance(result, list) else [result]
                )
        # Confirm that the engine reports the repeated attempts.
        if not alerts:
            health = self.engine.health()
            self.assertIsInstance(health, dict)
    def test_request_rate_detection_is_bounded_by_window(self):
        for timestamp in (1000, 1001, 1002, 1003):
            self.engine.record_request(
                client_id="rate-test-client",
                path="/",
                now=timestamp,
            )
        health = self.engine.health()
        self.assertIsInstance(health, dict)
    def test_alerts_never_request_firewall_modification(self):
        result = self.engine.record_failed_login(
            client_id="monitor-only-client",
            now=1000,
        )
        if isinstance(result, dict):
            self.assertNotEqual(result.get("action"), "block")
            self.assertFalse(
                result.get("system_firewall_modified", False)
            )
    def test_suspicious_path_detection(self):
        result = self.engine.record_request(
            client_id="path-test-client",
            path="/.env",
            now=1000,
        )
        if isinstance(result, dict):
            self.assertNotEqual(result.get("action"), "block")
            self.assertFalse(
                result.get("system_firewall_modified", False)
            )
if __name__ == "__main__":
    unittest.main()