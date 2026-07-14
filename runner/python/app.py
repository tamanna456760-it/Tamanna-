from flask import Flask, jsonify

app = Flask(__name__)


@app.route("/")
def home():
    return "Tamanna AI Running ✅"


@app.route("/api")
def api():
    return jsonify({"message": "Hello from Tamanna AI 🔥"})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000)
