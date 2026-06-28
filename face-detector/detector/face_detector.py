import cv2

face = cv2.CascadeClassifier(
    "models/haarcascade_frontalface_default.xml"
)

img = cv2.imread("test.jpg")

gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

faces = face.detectMultiScale(gray, 1.1, 4)

for (x, y, w, h) in faces:
    cv2.rectangle(img, (x, y), (x+w, y+h), (0,255,0), 2)

cv2.imshow("Face Detection", img)
cv2.waitKey(0)