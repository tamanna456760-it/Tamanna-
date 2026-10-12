"""Tests for Tamanna AI firewall threat detector."""
import unittest
from firewall.threat_detector import ThreatDetector
class TestThreatDetector(unittest.TestCase):
    def setUp(self):
        self.detector = ThreatDetector()
    def test_detector_initializes(self):
        """Threat detector should initialize successfully."""
        self.assertIsNotNone(self.detector)
    def test_suspicious_path_is_inspected(self):
        """A suspicious path should be inspected without crashing."""
        result = self.detector.inspect_path(
            client_id="test-client",
            path="/../../etc/passwd",
        )
        self.assertIsNotNone(result)
    def test_normal_path_is_inspected(self):
        """A normal path should be inspected without crashing."""
        result = self.detector.inspect_path(
            client_id="normal-client",
            path="/api/health",
        )
        self.assertIsNotNone(result)
    def test_repeated_failed_logins_are_handled(self):
        """Repeated failed-login events should be handled safely."""
        method = getattr(self.detector, "record_failed_login", None)
        if not callable(method):
            self.skipTest(
                "record_failed_login() is not exposed by this implementation."
            )
        for _ in range(3):
            method(client_id="login-test-client")
if __name__ == "__main__":
    unittest.main()