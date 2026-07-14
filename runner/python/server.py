import subprocess
import threading

from flask import Flask, jsonify

app = Flask(__name__)
building = False


def run_cmd(cmd):
    try:
        return subprocess.check_output(
            cmd, shell=True, stderr=subprocess.STDOUT, text=True
        )
    except subprocess.CalledProcessError as e:
        return e.output


@app.route("/build")
def build():
    global building

    if building:
        return jsonify({"log": "⏳ Build already running, please wait..."})

    building = True
    output = run_cmd("echo Building... && ls")
    building = False

    return jsonify({"log": "✔ Build completed successfully\n" + output})
