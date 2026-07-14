from encryptor import decrypt_file, encrypt_file
from face_auth import verify_face
from flask import Flask, render_template, request

app = Flask(__name__)

KNOWN_FACE = "database/my_face.jpg"


@app.route("/")
def home():
    return render_template("login.html")


@app.route("/unlock", methods=["POST"])
def unlock():

    file = request.files["image"]
    file.save("live.jpg")

    if verify_face(KNOWN_FACE, "live.jpg"):
        return {"status": "access granted"}
    else:
        return {"status": "denied"}


if __name__ == "__main__":
    app.run(debug=True)
