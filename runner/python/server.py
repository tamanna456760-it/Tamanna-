"""Small authenticated build-status endpoint for the runner."""

import hmac
import os
import subprocess
import threading

from flask import Flask, jsonify, request

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024
_build_lock = threading.Lock()


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

    if not _build_lock.acquire(blocking=False):
        return jsonify({"ok": False, "error": "build already running"}), 409

    try:
        result = subprocess.run(
            ["ls", "-la"],
            cwd=os.environ.get("TAMANNA_RUNNER_WORKDIR", "."),
            shell=False,
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
        return jsonify({
            "ok": result.returncode == 0,
            "log": result.stdout[-8000:],
            "error": result.stderr[-2000:],
            "returncode": result.returncode,
        }), (200 if result.returncode == 0 else 500)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return jsonify({"ok": False, "error": type(exc).__name__}), 500
    finally:
        _build_lock.release()
