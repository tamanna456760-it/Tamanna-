import cv2
import mediapipe as mp


class FaceAnalyzer:
    def __init__(self):
        self.face_detection = mp.solutions.face_detection.FaceDetection(
            model_selection=1, min_detection_confidence=0.5
        )

    def analyze(self, image_path):
        image = cv2.imread(image_path)

        if image is None:
            raise FileNotFoundError(image_path)

        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        results = self.face_detection.process(rgb)

        output = {"faces": 0, "detections": []}

        if results.detections:
            output["faces"] = len(results.detections)

            h, w, _ = image.shape

            for face in results.detections:

                box = face.location_data.relative_bounding_box

                x = int(box.xmin * w)
                y = int(box.ymin * h)
                bw = int(box.width * w)
                bh = int(box.height * h)

                cv2.rectangle(image, (x, y), (x + bw, y + bh), (0, 255, 0), 2)

                output["detections"].append(
                    {
                        "x": x,
                        "y": y,
                        "width": bw,
                        "height": bh,
                        "confidence": float(face.score[0]),
                    }
                )

        cv2.imwrite("static/uploads/result.jpg", image)

        return output
