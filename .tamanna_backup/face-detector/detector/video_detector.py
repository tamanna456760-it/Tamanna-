import os

import cv2

CASCADE_PATH = "models/haarcascade_frontalface_default.xml"

face_cascade = cv2.CascadeClassifier(CASCADE_PATH)


class VideoFaceDetector:

    def __init__(self):
        if face_cascade.empty():
            raise RuntimeError("Haar cascade model not loaded properly")

    def detect_from_video(
        self, video_path=None, output_path="static/uploads/output.mp4"
    ):

        # If video_path is None → use webcam
        cap = cv2.VideoCapture(0 if video_path is None else video_path)

        if not cap.isOpened():
            raise FileNotFoundError("Video source not found")

        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Video writer setup
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        fps = 20

        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

        face_count_total = 0

        while True:
            ret, frame = cap.read()

            if not ret:
                break

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            faces = face_cascade.detectMultiScale(
                gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
            )

            face_count_total += len(faces)

            for x, y, w, h in faces:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

                cv2.putText(
                    frame,
                    "Face",
                    (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0, 255, 0),
                    2,
                )

            out.write(frame)

            cv2.imshow("Video Face Detection", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

        cap.release()
        out.release()
        cv2.destroyAllWindows()

        return {"total_faces_detected": face_count_total, "output_video": output_path}


if __name__ == "__main__":
    detector = VideoFaceDetector()

    result = detector.detect_from_video("test.mp4")

    print(result)
