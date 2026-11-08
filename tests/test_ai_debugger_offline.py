import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from ai_debugger import build_offline_review


class OfflineDiagnosticTests(unittest.TestCase):
    def test_groups_scanner_findings_without_inventing_them(self):
        source = "\n".join(
            [
                "[ERROR] app.py:4 - Python syntax error",
                "[REVIEW] config.yml:8 - Possible hard-coded API key/secret",
                "[INFO] app.py:10 - TODO/FIXME marker found",
            ]
        )

        result = build_offline_review(source)

        self.assertIn("[ERROR] app.py:4 - Python syntax error", result)
        self.assertIn("[REVIEW] config.yml:8 - Possible hard-coded API key/secret", result)
        self.assertIn("ERROR: 1", result)
        self.assertIn("REVIEW: 1", result)
        self.assertIn("INFO: 1", result)
        self.assertNotIn("invented vulnerability", result.lower())

    def test_empty_findings_are_reported_as_empty(self):
        result = build_offline_review("Scanner finished. No findings.")
        self.assertIn("No scanner errors were reported.", result)
        self.assertIn("REVIEW: 0", result)


if __name__ == "__main__":
    unittest.main()
