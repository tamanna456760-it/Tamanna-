import cv2
import numpy as np
import os

CASCADE_PATH = "models/haarcascade_frontalface_default.xml"

AGE_MODEL_PATH = "models/age.onnx"
GENDER_MODEL_PATH = "models/gender.onnx"

AGE_BUCKETS = [
    "(0-2)", "(4-6)", "(8-12)", "(15-20)",
    "(25-32)", "(38-43)", "(48-53)", "(60-100)"
]

GENDERS = ["Male", "Female"]


class AgeGenderDetector:

    def __init__(self):

        self.face_cascade = cv2.CascadeClassifier(CASCADE_PATH)

        self.age_net = None
        self.gender_net = None

        if os.path.exists(AGE_MODEL_PATH):
            self.age_net = cv2.dnn.readNetFromONNX(AGE_MODEL_PATH)

        if os.path.exists(GENDER_MODEL_PATH):
            self.gender_net = cv2.dnn.readNetFromONNX(GENDER_MODEL_PATH)

    def detect(self, image_path, output_path="static/uploads/age_gender.jpg"):

        image = cv2.imread(image_path)

        if image is None:
            raise FileNotFoundError(image_path)

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30)
        )

        results = []

        for (x, y, w, h) in faces:

            face = image[y:y+h, x:x+w]

            blob = cv2.dnn.blobFromImage(
                face,
                scalefactor=1.0,
                size=(227, 227),
                mean=(78.426, 87.768, 114.895),
                swapRB=False
            )

            # Default values
            age = "Unknown"
            gender = "Unknown"

            # Gender prediction
            if self.gender_net is not None:
                self.gender_net.setInput(blob)
                gender_preds = self.gender_net.forward()[0]
                gender = GENDERS[int(np.argmax(gender_preds))]

            # Age prediction
            if self.age_net is not None:
                self.age_net.setInput(blob)
                age_preds = self.age_net.forward()[0]
                age = AGE_BUCKETS[int(np.argmax(age_preds))]

            cv2.rectangle(image, (x, y), (x+w, y+h), (0,255,0), 2)

            label = f"{gender}, {age}"

            cv2.putText(
                image,
                label,
                (x, y-10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0,255,0),
                2
            )

            results.append({
                "gender": gender,
                "age": age,
                "box": [x, y, w, h]
            })

        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        cv2.imwrite(output_path, image)

        return {
            "faces": len(results),
            "results": results,
            "output": output_path
        }


if __name__ == "__main__":

    detector = AgeGenderDetector()

    print(detector.detect("test.jpg"))