from flask import Flask, jsonify
import subprocess

app = Flask(__name__)

def run_cmd(cmd):
    try:
        output = subprocess.check_output(
            cmd, shell=True, stderr=subprocess.STDOUT, text=True
        )
        return output
    except subprocess.CalledProcessError as e:
        return e.output

@app.route("/connect")
def connect():
    return jsonify({"log": "✔ Connected to local system & git repo"})

@app.route("/fix")
def fix():
    output = run_cmd("git status")
    return jsonify({"log": "✔ Files scanned\n" + output})

@app.route("/save")
def save():
    output = run_cmd("git add . && git commit -m 'Auto save by Tamanna System'")
    return jsonify({"log": output})

@app.route("/build")
def build():
    output = run_cmd("echo Building project... && ls")
    return jsonify({"log": output})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)