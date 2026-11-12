"""Tests for the optional ClamAV malware scanner."""
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from endpoint_security.antivirus import AntivirusScanner


class AntivirusScannerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.sample = Path(self.temp.name) / "sample.txt"
        self.sample.write_text("Tamanna AI test file", encoding="utf-8")

    @patch("endpoint_security.antivirus.shutil.which", return_value=None)
    def test_reports_engine_unavailable_without_clamav(self, _which):
        result = AntivirusScanner().scan_file(self.sample)
        self.assertEqual(result["status"], "engine_unavailable")

    @patch("endpoint_security.antivirus.subprocess.run")
    @patch("endpoint_security.antivirus.shutil.which", return_value="/usr/bin/clamscan")
    def test_clean_file(self, run, _which):
        run.return_value = Mock(returncode=0, stdout="sample: OK", stderr="")
        result = AntivirusScanner().scan_file(self.sample)
        self.assertEqual(result["status"], "clean")
        self.assertEqual(run.call_args.args[0][0], "/usr/bin/clamscan")

    @patch("endpoint_security.antivirus.subprocess.run")
    @patch("endpoint_security.antivirus.shutil.which", return_value="/usr/bin/clamscan")
    def test_infected_file(self, run, _which):
        run.return_value = Mock(
            returncode=1,
            stdout="sample: Eicar-Test-Signature FOUND",
            stderr="",
        )
        result = AntivirusScanner().scan_file(self.sample)
        self.assertEqual(result["status"], "infected")
        self.assertIn("Eicar-Test-Signature", result["message"])

    @patch("endpoint_security.antivirus.shutil.which", return_value="/usr/bin/clamscan")
    @patch("endpoint_security.antivirus.subprocess.run",
           side_effect=subprocess.TimeoutExpired("clamscan", 1))
    def test_timeout_is_reported(self, _run, _which):
        result = AntivirusScanner(timeout_seconds=1).scan_file(self.sample)
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["message"], "scan timed out")

    def test_oversized_file_is_skipped(self):
        result = AntivirusScanner(max_file_size_bytes=1).scan_file(self.sample)
        self.assertEqual(result["status"], "skipped")

    def test_symlink_is_not_followed(self):
        link = Path(self.temp.name) / "sample-link"
        try:
            link.symlink_to(self.sample)
        except (OSError, NotImplementedError):
            self.skipTest("symlinks are unavailable")
        result = AntivirusScanner().scan_file(link)
        self.assertEqual(result["status"], "skipped")

    def test_rejects_invalid_limits(self):
        with self.assertRaises(ValueError):
            AntivirusScanner(timeout_seconds=0)
        with self.assertRaises(ValueError):
            AntivirusScanner(max_file_size_bytes=-1)


if __name__ == "__main__":
    unittest.main()
