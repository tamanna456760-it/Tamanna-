import tempfile
import unittest
from pathlib import Path

from tamanna_ai.security.ethical_audit import run_ethical_audit


class EthicalAuditTests(unittest.TestCase):
    def test_audit_reports_review_when_required_config_is_missing(self):
        with tempfile.TemporaryDirectory() as directory:
            report = run_ethical_audit(Path(directory))
        self.assertEqual(report["mode"], "read_only")
        self.assertEqual(report["summary"]["status"], "REVIEW_REQUIRED")
        self.assertEqual(report["summary"]["total"], 4)

    def test_audit_never_claims_network_scan(self):
        with tempfile.TemporaryDirectory() as directory:
            report = run_ethical_audit(Path(directory))
        self.assertTrue(any("No network requests" in item for item in report["limitations"]))


if __name__ == "__main__":
    unittest.main()
