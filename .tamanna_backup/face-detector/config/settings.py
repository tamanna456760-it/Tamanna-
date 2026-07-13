"""
config/settings.py
Application configuration for Face Detector
"""

import os

# =========================
# Flask Settings
# =========================

DEBUG = True
HOST = "0.0.0.0"
PORT = 5000

SECRET_KEY = os.getenv("SECRET_KEY", "change-this-secret-key")

# =========================
# Upload Settings
# =========================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")

MAX_CONTENT_LENGTH = 20 * 1024 * 1024  # 20 MB

ALLOWED_EXTENSIONS = {
    "jpg",
    "jpeg",
    "png",
    "bmp",
    "webp",
    "mp4",
    "avi",
    "mov"
}

# =========================
# OpenCV Model
# =========================

CASCADE_PATH = os.path.join(
    BASE_DIR,
    "models",
    "haarcascade_frontalface_default.xml"
)

# =========================
# Detection Settings
# =========================

SCALE_FACTOR = 1.1
MIN_NEIGHBORS = 5
MIN_SIZE = (30, 30)

# =========================
# Drawing Settings
# =========================

RECTANGLE_COLOR = (0, 255, 0)
RECTANGLE_THICKNESS = 2

# =========================
# Camera
# =========================

CAMERA_INDEX = 0

# =========================
# Supported File Types
# =========================

IMAGE_EXTENSIONS = (
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp",
    ".webp"
)

VIDEO_EXTENSIONS = (
    ".mp4",
    ".avi",
    ".mov"
)