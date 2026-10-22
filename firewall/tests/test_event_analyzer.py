"""
Tamanna AI Firewall - Event Analyzer Tests
Owner: HM INSAN ALI
"""
import unittest
from firewall.event_analyzer import analyze_events
class TestEventAnalyzer(unittest.TestCase):
    def test_empty_events_return_zero_counts(self):
        report = analyze_events([])
        self.assertEqual(report["total_events"], 0)
        self.assertEqual(report["high_risk_events"], 0)
        self.assertEqual(report["suspicious_events"], 0)
    def test_counts_events_by_severity(self):
        events = [
            {"event_type": "login", "severity": "INFO"},
            {"event_type": "login_failed", "severity": "HIGH"},
            {"event_type": "request", "severity": "CRITICAL"},
            {"event_type": "request", "severity": "LOW"},
        ]
        report = analyze_events(events)
        self.assertEqual(report["total_events"], 4)
        self.assertEqual(report["severity_counts"]["INFO"], 1)
        self.assertEqual(report["severity_counts"]["HIGH"], 1)
        self.assertEqual(report["severity_counts"]["CRITICAL"], 1)
        self.assertEqual(report["severity_counts"]["LOW"], 1)
        self.assertEqual(report["high_risk_events"], 2)
    def test_counts_event_types(self):
        events = [
            {"event_type": "login_failed", "severity": "MEDIUM"},
            {"event_type": "login_failed", "severity": "HIGH"},
            {"event_type": "request_received", "severity": "INFO"},
        ]
        report = analyze_events(events)
        self.assertEqual(report["event_type_counts"]["login_failed"], 2)
        self.assertEqual(report["event_type_counts"]["request_received"], 1)
    def test_suspicious_keywords_are_counted(self):
        events = [
            {"event_type": "login_failed", "severity": "MEDIUM"},
            {"event_type": "unauthorized_access", "severity": "HIGH"},
            {"event_type": "request_received", "severity": "INFO"},
        ]
        report = analyze_events(events)
        self.assertEqual(report["suspicious_events"], 2)
    def test_severity_matching_is_case_insensitive(self):
        events = [
            {"event_type": "security_alert", "severity": "critical"},
        ]
        report = analyze_events(events)
        self.assertEqual(report["high_risk_events"], 1)
        self.assertEqual(report["severity_counts"]["CRITICAL"], 1)
    def test_non_dictionary_entries_are_ignored(self):
        events = [
            {"event_type": "valid_event", "severity": "INFO"},
            None,
            "invalid-entry",
        ]
        report = analyze_events(events)
        self.assertEqual(report["total_events"], 1)
    def test_non_list_input_is_rejected(self):
        with self.assertRaises(TypeError):
            analyze_events({"event_type": "test"})
    def test_report_does_not_claim_to_modify_firewall(self):
        report = analyze_events([])
        self.assertFalse(report["system_firewall_modified"])
        self.assertIn("generated_at", report)
        self.assertEqual(report["project"], "Tamanna AI")
if __name__ == "__main__":
    unittest.main(verbosity=2)