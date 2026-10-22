"""Unit tests for Tamanna AI readiness checker.
Owner: HM INSAN ALI
"""
import tempfile
import unittest
from pathlib import Path
from endpoint_security.readiness_check import check_readiness
class TestReadinessChecker(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
    def tearDown(self):
        self.temp_dir.cleanup()
    def create_file(self, relative_path, content="test content"):
        path = self.root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path
    def test_all_required_files_present(self):
        from endpoint_security.readiness_check import REQUIRED_FILES
        for relative_path in REQUIRED_FILES:
            self.create_file(relative_path)
        result = check_readiness(self.root)
        self.assertEqual(
            result["summary"]["readiness"],
            "FILES_PRESENT",
        )
        self.assertEqual(result["summary"]["missing"], 0)
        self.assertEqual(result["summary"]["empty"], 0)
    def test_missing_files_require_action(self):
        result = check_readiness(self.root)
        self.assertEqual(
            result["summary"]["readiness"],
            "ACTION_REQUIRED",
        )
        self.assertGreater(result["summary"]["missing"], 0)
    def test_empty_file_is_detected(self):
        from endpoint_security.readiness_check import REQUIRED_FILES
        first_file = REQUIRED_FILES[0]
        self.create_file(first_file, content="")
        result = check_readiness(self.root)
        self.assertEqual(result["summary"]["empty"], 1)
        self.assertEqual(
            result["summary"]["readiness"],
            "ACTION_REQUIRED",
        )
    def test_nonempty_file_is_present(self):
        from endpoint_security.readiness_check import REQUIRED_FILES
        self.create_file(REQUIRED_FILES[0], content="{}")
        result = check_readiness(self.root)
        self.assertEqual(result["checks"][0]["status"], "PRESENT")
        self.assertEqual(result["summary"]["present"], 1)
    def test_summary_counts_match_checks(self):
        from endpoint_security.readiness_check import REQUIRED_FILES
        self.create_file(REQUIRED_FILES[0], content="sample")
        self.create_file(REQUIRED_FILES[1], content="")
        result = check_readiness(self.root)
        summary = result["summary"]
        self.assertEqual(
            summary["total"],
            summary["present"] + summary["missing"] + summary["empty"],
        )
        self.assertEqual(summary["empty"], 1)
if __name__ == "__main__":
    unittest.main(verbosity=2)