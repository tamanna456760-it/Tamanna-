import datetime

from flask import Flask, request

app = Flask(__name__)


@app.before_request
def log_request():
    with open("security.log", "a", encoding="utf-8") as f:
        f.write(
            f"{datetime.datetime.now()} | "
            f"IP={request.remote_addr} | "
            f"METHOD={request.method} | "
            f"PATH={request.path} | "
            f"UA={request.headers.get('User-Agent')}\n"
        )


@app.route("/")
def home():
    return "OK"


app.run(host="0.0.0.0", port=5000)
