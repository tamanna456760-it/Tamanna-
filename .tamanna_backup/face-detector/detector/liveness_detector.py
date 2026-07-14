import os

import cv2
import numpy as np

MODEL_PATH = "models/liveness.onnx"


class LivenessDetector:

    def __init__(self):
        self.model = None

        if os.path.exists(MODEL_PATH):
            self.model = cv2.dnn.readNetFromONNX(MODEL_PATH)

    def detect(self, image_path):

        img = cv2.imread(image_path)

        if self.model is None:
            return {"liveness": "Unknown (No model)"}

        blob = cv2.dnn.blobFromImage(img, 1 / 255.0, (96, 96))
        self.model.setInput(blob)
        pred = self.model.forward()[0]

        label = "Real" if np.argmax(pred) == 1 else "Fake"

        return {"liveness": label}
