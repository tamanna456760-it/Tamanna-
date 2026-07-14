from flask import Flask, jsonify, request

app = Flask(__name__)


# Simple AI brain
def ai_reply(message):
    message = message.lower()

    if "hello" in message:
        return "Hi! 👋 How can I help you?"
    elif "name" in message:
        return "I am Tamanna AI 🤖"
    elif "how are you" in message:
        return "I am fine! You?"
    else:
        return "You said: " + message


@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    msg = data.get("message")

    reply = ai_reply(msg)
    return jsonify({"reply": reply})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
