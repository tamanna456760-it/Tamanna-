import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from endpoint_security.cyber_security_center import run_center


class CyberSecurityCenterTests(unittest.TestCase):
    @patch("endpoint_security.cyber_security_center.check_requirements")
    @patch("endpoint_security.cyber_security_center.run_ethical_audit")
    def test_local_audit_does_not_request_network_check(self, audit, dependencies):
        audit.return_value = {"summary": {"status": "PASS"}}
        dependencies.return_value = {"status": "PASS"}
        with tempfile.TemporaryDirectory() as directory:
            result = run_center(directory)
        self.assertEqual(result["summary"]["status"], "PASS")
        self.assertFalse(result["network_checks_requested"])
        self.assertEqual(len(result["checks"]), 2)

    @patch("endpoint_security.cyber_security_center.check_tls_certificate")
    @patch("endpoint_security.cyber_security_center.check_requirements")
    @patch("endpoint_security.cyber_security_center.run_ethical_audit")
    def test_tls_runs_only_for_explicit_hostname(self, audit, dependencies, tls):
        audit.return_value = {"summary": {"status": "PASS"}}
        dependencies.return_value = {"status": "PASS"}
        tls.return_value = {"status": "PASS", "hostname": "example.com"}
        with tempfile.TemporaryDirectory() as directory:
            result = run_center(directory, "example.com", 443)
        tls.assert_called_once_with("example.com", port=443)
        self.assertTrue(result["network_checks_requested"])
        self.assertEqual(result["summary"]["total"], 3)

    def test_rejects_url_instead_of_hostname(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(ValueError):
                run_center(directory, "https://example.com")

    def test_rejects_invalid_tls_port(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(ValueError):
                run_center(directory, "example.com", 70000)


if __name__ == "__main__":
    unittest.main()
