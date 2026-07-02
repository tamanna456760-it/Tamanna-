# detector/face_mesh.py

import cv2
import mediapipe as mp
import os

mp_face_mesh = mp.solutions.face_mesh
mp_drawing = mp.solutions.drawing_utils
mp_styles = mp.solutions.drawing_styles


class FaceMeshDetector:

    def __init__(
        self,
        static_image_mode=True,
        max_num_faces=5,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
    ):

        self.face_mesh = mp_face_mesh.FaceMesh(
            static_image_mode=static_image_mode,
            max_num_faces=max_num_faces,
            refine_landmarks=True,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence,
        )

    def detect(self, image_path, output_path="static/uploads/face_mesh_result.jpg"):

        image = cv2.imread(image_path)

        if image is None:
            raise FileNotFoundError(image_path)

        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        results = self.face_mesh.process(rgb)

        face_count = 0

        if results.multi_face_landmarks:

            face_count = len(results.multi_face_landmarks)

            for face_landmarks in results.multi_face_landmarks:

                mp_drawing.draw_landmarks(
                    image=image,
                    landmark_list=face_landmarks,
                    connections=mp_face_mesh.FACEMESH_TESSELATION,
                    landmark_drawing_spec=None,
                    connection_drawing_spec=mp_styles.get_default_face_mesh_tesselation_style(),
                )

                mp_drawing.draw_landmarks(
                    image=image,
                    landmark_list=face_landmarks,
                    connections=mp_face_mesh.FACEMESH_CONTOURS,
                    landmark_drawing_spec=None,
                    connection_drawing_spec=mp_styles.get_default_face_mesh_contours_style(),
                )

        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        cv2.imwrite(output_path, image)

        return {
            "faces": face_count,
            "output": output_path
        }


if __name__ == "__main__":

    detector = FaceMeshDetector()

    result = detector.detect("test.jpg")

    print(result)