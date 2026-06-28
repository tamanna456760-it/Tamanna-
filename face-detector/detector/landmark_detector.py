# detector/landmark_detector.py

import cv2
import mediapipe as mp
import os

mp_face_mesh = mp.solutions.face_mesh


class LandmarkDetector:
    def __init__(self):
        self.face_mesh = mp_face_mesh.FaceMesh(
            static_image_mode=True,
            max_num_faces=5,
            refine_landmarks=True,
            min_detection_confidence=0.5,
        )

    def detect(self, image_path, output_path="static/uploads/landmarks.jpg"):

        image = cv2.imread(image_path)

        if image is None:
            raise FileNotFoundError(image_path)

        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        results = self.face_mesh.process(rgb)

        h, w, _ = image.shape

        faces = []

        if results.multi_face_landmarks:

            for face in results.multi_face_landmarks:

                landmarks = []

                for point in face.landmark:

                    x = int(point.x * w)
                    y = int(point.y * h)

                    landmarks.append({
                        "x": x,
                        "y": y
                    })

                    cv2.circle(
                        image,
                        (x, y),
                        1,
                        (0, 255, 0),
                        -1
                    )

                faces.append(landmarks)

        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        cv2.imwrite(output_path, image)

        return {
            "face_count": len(faces),
            "landmarks": faces,
            "output": output_path
        }


if __name__ == "__main__":

    detector = LandmarkDetector()

    result = detector.detect("test.jpg")

    print(result)