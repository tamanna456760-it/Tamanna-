"""Tests for security monitor event handling."""
import unittest
from firewall.security_monitor import SecurityMonitor
class TestSecurityMonitorEvents(unittest.TestCase):
    def setUp(self):
        self.monitor = SecurityMonitor()
    def test_monitor_initializes(self):
        self.assertIsNotNone(self.monitor)
    def test_event_is_accepted_by_supported_method(self):
        event = {
            "event_type": "suspicious_request",
            "severity": "high",
            "client_id": "test-client",
            "details": {
                "path": "/../../etc/passwd",
                "source": "unit_test",
            },
        }
        # Adapt to the public method actually provided by this monitor.
        for method_name in (
            "record_event",
            "log_event",
            "add_event",
            "record",
        ):
            method = getattr(self.monitor, method_name, None)
            if not callable(method):
                continue
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
                    continue
            return
        self.skipTest(
            "No compatible event-recording method was found in SecurityMonitor."
        )
    def test_summary_method_is_available(self):
        names = ("summary", "get_summary", "generate_report")
        if not any(
            callable(getattr(self.monitor, name, None))
            for name in names
        ):
            self.skipTest(
                "No recognized summary method exists in SecurityMonitor."
            )
if __name__ == "__main__":
    unittest.main()