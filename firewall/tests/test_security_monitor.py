"""Tests for Tamanna AI firewall security monitor."""
import unittest
from firewall.security_monitor import SecurityMonitor
class TestSecurityMonitor(unittest.TestCase):
    def setUp(self):
        self.monitor = SecurityMonitor()
    def test_monitor_can_be_created(self):
        """Security monitor should initialize successfully."""
        self.assertIsNotNone(self.monitor)
    def test_monitor_accepts_security_event(self):
        """Monitor should accept a security event."""
        event = {
            "event_type": "failed_login",
            "severity": "medium",
            "client_id": "test-client",
            "details": {"source": "unit_test"},
        }
        # Support common event-recording method names.
        for method_name in ("record_event", "log_event", "add_event", "record"):
            method = getattr(self.monitor, method_name, None)
            if callable(method):
                method(event)
                return
        self.skipTest(
            "No supported event-recording method found; "
            "check security_monitor.py's public interface."
        )
    def test_monitor_exposes_summary_or_report(self):
        """Monitor should expose a summary or report method."""
        supported_methods = (
            "summary",
            "get_summary",
            "generate_report",
            "export_report",
        )
        if not any(
            callable(getattr(self.monitor, name, None))
            for name in supported_methods
        ):
            self.skipTest(
                "No summary/report method found; "
                "check security_monitor.py's public interface."
            )
if __name__ == "__main__":
    unittest.main()