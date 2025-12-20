from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/status")
def status():
    return jsonify({"network": "connected"})

@app.route("/devices")
def devices():
    return jsonify([
        {"name": "Phone", "ip": "192.168.1.2"},
        {"name": "Laptop", "ip": "192.168.1.5"}
    ])

app.run(host="0.0.0.0", port=5000)