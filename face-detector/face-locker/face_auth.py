import cv2
import face_recognition


def verify_face(known_image, live_image):
    known = face_recognition.load_image_file(known_image)
    live = face_recognition.load_image_file(live_image)

    known_enc = face_recognition.face_encodings(known)
    live_enc = face_recognition.face_encodings(live)

    if len(known_enc) == 0 or len(live_enc) == 0:
        return False

    result = face_recognition.compare_faces([known_enc[0]], live_enc[0])

    return result[0]
