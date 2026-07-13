import cv2
import numpy as np

class QualityChecker:

    def analyze(self, image_path):

        img = cv2.imread(image_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        blur = cv2.Laplacian(gray, cv2.CV_64F).var()
        brightness = np.mean(gray)

        quality = "High"

        if blur < 50:
            quality = "Low (Blurry)"

        if brightness < 60:
            quality = "Dark"

        if brightness > 200:
            quality = "Overexposed"

        return {
            "blur_score": float(blur),
            "brightness": float(brightness),
            "quality": quality
        }