"""Local diagnostic Flask endpoint. It executes no user-supplied commands."""
import os
import subprocess
from flask import Flask, jsonify

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 1024
BUILDING = False


@app.get("/health")
def health():
    return jsonify({"status": "ok", "mode": "read_only"})


@app.post("/build")
def build():
    global BUILDING
    if os.getenv("TAMANNA_ENABLE_LOCAL_BUILD_ENDPOINT", "").lower() != "true":
        return jsonify({"error": "local build endpoint is disabled"}), 403
    if BUILDING:
        return jsonify({"log": "Build already running"}), 409
    BUILDING = True
    try:
        result = subprocess.run(["python", "--version"], capture_output=True, text=True, timeout=5, check=False)
        return jsonify({"status": "diagnostic_complete" if result.returncode == 0 else "failed", "log": (result.stdout + result.stderr)[:4000]}), 200 if result.returncode == 0 else 500
    except (OSError, subprocess.TimeoutExpired) as exc:
        return jsonify({"error": type(exc).__name__}), 500
    finally:
        BUILDING = False
