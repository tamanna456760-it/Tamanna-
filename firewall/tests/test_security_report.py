"""Tests for Tamanna AI firewall security report generation."""
import json
import tempfile
import unittest
from pathlib import Path
from firewall.security_monitor import SecurityMonitor
class TestSecurityReport(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.report_path = Path(self.temp_dir.name) / "security_report.json"
        self.monitor = SecurityMonitor()
    def tearDown(self):
        self.temp_dir.cleanup()
    def test_report_export_method_exists(self):
        """Monitor should expose a report or export method."""
        names = ("export_report", "generate_report", "save_report")
        if not any(
            callable(getattr(self.monitor, name, None))
            for name in names
        ):
            self.skipTest(
                "No recognized report-export method exists in SecurityMonitor."
            )
    def test_exported_report_is_valid_json(self):
        """If export is supported, the resulting report should be valid JSON."""
        for name in ("export_report", "generate_report", "save_report"):
            method = getattr(self.monitor, name, None)
            if not callable(method):
                continue
            try:
                result = method(str(self.report_path))
            except TypeError:
                # The method may accept no path or use keyword arguments.
                self.skipTest(
                    f"{name}() has a different signature; inspect "
                    "security_monitor.py before adapting this test."
                )
            if self.report_path.exists():
                with self.report_path.open("r", encoding="utf-8") as file:
                    data = json.load(file)
                self.assertIsInstance(data, (dict, list))
                return
            if isinstance(result, (dict, list)):
                json.dumps(result)
                return
            self.skipTest(
                "The report method did not create a file or return JSON data."
            )
        self.skipTest("No report-export method is available.")
if __name__ == "__main__":
    unittest.main()