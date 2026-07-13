import cv2
import numpy as np
import os

CASCADE_PATH = "models/haarcascade_frontalface_default.xml"
MODEL_PATH = "models/mask.onnx"

LABELS = ["Mask", "No Mask"]


class MaskDetector:

    def __init__(self):
        self.face = cv2.CascadeClassifier(CASCADE_PATH)
        self.model = None

        if os.path.exists(MODEL_PATH):
            self.model = cv2.dnn.readNetFromONNX(MODEL_PATH)

    def detect(self, image_path, output="static/uploads/mask.jpg"):

        img = cv2.imread(image_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        faces = self.face.detectMultiScale(gray, 1.1, 5)

        results = []

        for (x, y, w, h) in faces:

            label = "Unknown"

            if self.model:
                face = img[y:y+h, x:x+w]
                blob = cv2.dnn.blobFromImage(face, 1/255.0, (100,100))
                self.model.setInput(blob)
                pred = self.model.forward()[0]
                label = LABELS[int(np.argmax(pred))]

            cv2.rectangle(img, (x,y),(x+w,y+h),(0,255,0),2)
            cv2.putText(img, label, (x,y-10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7,(0,255,0),2)

            results.append({"mask": label})

        os.makedirs("static/uploads", exist_ok=True)
        cv2.imwrite(output, img)

        return {"faces": len(results), "results": results}