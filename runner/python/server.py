"""Authenticated runner API.

The build endpoint intentionally returns 501 until a real, isolated build
executor is configured. It must never report a directory listing as a build.
"""

import hmac
import os

from flask import Flask, jsonify, request

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024


def _authorized() -> bool:
    expected = os.environ.get("TAMANNA_RUNNER_API_KEY", "")
    supplied = request.headers.get("X-API-KEY", "")
    return bool(expected and supplied and hmac.compare_digest(expected, supplied))


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"ok": True, "service": "tamanna-runner"})


@app.route("/build", methods=["POST"])
def build():
    if not _authorized():
        return jsonify({"ok": False, "error": "unauthorized"}), 401

    return jsonify({
        "ok": False,
        "error": "build executor is not configured",
        "status": "not_implemented",
    }), 501
