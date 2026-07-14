"""
tests/test_detector.py

Basic tests for the Face Detector project.
"""

import os
import unittest

import cv2
from detector.face_detector import detect_faces


class TestFaceDetector(unittest.TestCase):

    def test_model_exists(self):
        """Check that the Haar Cascade model file exists."""
        self.assertTrue(os.path.exists("models/haarcascade_frontalface_default.xml"))

    def test_opencv_loaded(self):
        """Check that OpenCV is installed."""
        self.assertIsNotNone(cv2.__version__)

    def test_invalid_image(self):
        """detect_faces should raise FileNotFoundError for a missing image."""
        with self.assertRaises(FileNotFoundError):
            detect_faces("does_not_exist.jpg")


if __name__ == "__main__":
    unittest.main()
