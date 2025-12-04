from flask import Flask, request, jsonify
import hashlib
import time

app = Flask(__name__)

# In-memory sync database
sync_store = {}

def generate_version():
    return hashlib.sha256(str(time.time()).encode()).hexdigest()

@app.route("/sync/get", methods=["POST"])
def get_data():
    device_id = request.json.get("device_id")
    key = request.json.get("key")

    if key in sync_store:
        return jsonify(sync_store[key])
    return jsonify({"exists": False})

@app.route("/sync/set", methods=["POST"])
def set_data():
    device_id = request.json.get("device_id")
    key = request.json.get("key")
    value = request.json.get("value")

    sync_store[key] = {
        "value": value,
        "last_update": time.time(),
        "version": generate_version(),
        "device": device_id
    }

    return jsonify({"synced": True, "version": sync_store[key]["version"]})

@app.route("/sync/list", methods=["GET"])
def list_keys():
    return jsonify({"keys": list(sync_store.keys())})

if __name__ == "__main__":
    app.run(debug=True)