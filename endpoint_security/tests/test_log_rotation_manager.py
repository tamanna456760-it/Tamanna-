"""Unit tests for Tamanna AI log rotation status checker.
Owner: HM INSAN ALI
"""
import tempfile
import unittest
from pathlib import Path
from endpoint_security.log_rotation_manager import get_rotation_status
class TestLogRotationManager(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.log_path = Path(self.temp_dir.name) / "events.jsonl"
    def tearDown(self):
        self.temp_dir.cleanup()
    def test_missing_log_is_reported(self):
        result = get_rotation_status(self.log_path, max_bytes=100)
        self.assertTrue(result["valid"])
        self.assertEqual(result["status"], "MISSING")
        self.assertFalse(result["rotation_needed"])
    def test_small_log_does_not_need_rotation(self):
        self.log_path.write_bytes(b"12345")
        result = get_rotation_status(self.log_path, max_bytes=10)
        self.assertTrue(result["valid"])
        self.assertEqual(result["status"], "OK")
        self.assertEqual(result["size_bytes"], 5)
        self.assertFalse(result["rotation_needed"])
    def test_threshold_reached_recommends_rotation(self):
        self.log_path.write_bytes(b"1234567890")
        result = get_rotation_status(self.log_path, max_bytes=10)
        self.assertEqual(result["status"], "ROTATION_RECOMMENDED")
        self.assertTrue(result["rotation_needed"])
        self.assertFalse(result["action_taken"])
    def test_larger_than_threshold_recommends_rotation(self):
        self.log_path.write_bytes(b"x" * 25)
        result = get_rotation_status(self.log_path, max_bytes=10)
        self.assertTrue(result["rotation_needed"])
        self.assertEqual(result["size_bytes"], 25)
    def test_zero_threshold_is_rejected(self):
        result = get_rotation_status(self.log_path, max_bytes=0)
        self.assertFalse(result["valid"])
        self.assertEqual(result["status"], "INVALID_THRESHOLD")
    def test_negative_threshold_is_rejected(self):
        result = get_rotation_status(self.log_path, max_bytes=-1)
        self.assertFalse(result["valid"])
    def test_directory_path_is_rejected(self):
        result = get_rotation_status(
            Path(self.temp_dir.name),
            max_bytes=100,
        )
        self.assertFalse(result["valid"])
        self.assertEqual(result["status"], "INVALID_PATH")
if __name__ == "__main__":
    unittest.main(verbosity=2)