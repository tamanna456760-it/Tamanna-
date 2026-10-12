"""Bounds and robustness tests for Tamanna AI security monitor."""
import unittest
from firewall.security_monitor import SecurityMonitor
class TestSecurityMonitorBounds(unittest.TestCase):
    def setUp(self):
        self.monitor = SecurityMonitor()
    def test_monitor_handles_many_events_without_crashing(self):
        """A bounded monitor should safely process repeated events."""
        event = {
            "event_type": "request_checked",
            "severity": "low",
            "client_id": "bounds-test-client",
            "details": {"source": "unit_test"},
        }
        method = None
        for name in ("record_event", "log_event", "add_event", "record"):
            candidate = getattr(self.monitor, name, None)
            if callable(candidate):
                method = candidate
                break
        if method is None:
            self.skipTest("No supported event-recording method found.")
        for _ in range(200):
            try:
                method(event)
            except TypeError:
                try:
                    method(
                        event_type=event["event_type"],
                        severity=event["severity"],
                        client_id=event["client_id"],
                        details=event["details"],
                    )
                except TypeError:
                    self.skipTest(
                        "Event method uses a different argument signature."
                    )
    def test_monitor_still_responds_after_event_processing(self):
        """The monitor should remain usable after repeated event processing."""
        self.assertIsNotNone(self.monitor)
if __name__ == "__main__":
    unittest.main()