# detector/emotion_detector.py

import cv2
import numpy as np
import os

EMOTIONS = [
    "Angry",
    "Disgust",
    "Fear",
    "Happy",
    "Sad",
    "Surprise",
    "Neutral"
]


class EmotionDetector:

    def __init__(
        self,
        cascade_path="models/haarcascade_frontalface_default.xml",
        model_path="models/emotion.onnx"
    ):

        self.face_detector = cv2.CascadeClassifier(cascade_path)

        self.model = None

        if os.path.exists(model_path):
            self.model = cv2.dnn.readNetFromONNX(model_path)

    def detect(self, image_path):

        image = cv2.imread(image_path)

        if image is None:
            raise FileNotFoundError(image_path)

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        faces = self.face_detector.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5
        )

        results = []

        for (x, y, w, h) in faces:

            emotion = "Unknown"
            confidence = 0.0

            if self.model is not None:

                face = gray[y:y+h, x:x+w]

                face = cv2.resize(face, (64, 64))

                blob = cv2.dnn.blobFromImage(
                    face,
                    scalefactor=1/255.0,
                    size=(64,64)
                )

                self.model.setInput(blob)

                prediction = self.model.forward()[0]

                idx = int(np.argmax(prediction))

                emotion = EMOTIONS[idx]

                confidence = float(prediction[idx])

            cv2.rectangle(
                image,
                (x, y),
                (x+w, y+h),
                (0,255,0),
                2
            )

            cv2.putText(
                image,
                emotion,
                (x, y-10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0,255,0),
                2
            )

            results.append({
                "emotion": emotion,
                "confidence": confidence,
                "box": [x, y, w, h]
            })

        os.makedirs("static/uploads", exist_ok=True)

        output = "static/uploads/emotion_result.jpg"

        cv2.imwrite(output, image)

        return {
            "faces": len(results),
            "results": results,
            "output": output
        }


if __name__ == "__main__":

    detector = EmotionDetector()

    print(detector.detect("test.jpg"))