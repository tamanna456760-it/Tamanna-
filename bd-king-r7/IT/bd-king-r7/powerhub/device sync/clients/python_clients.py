import requests
import json

SERVER = "http://127.0.0.1:5000"

DEVICE_ID = "device_01"  # change per device

def sync_set(key, value):
    payload = {
        "device_id": DEVICE_ID,
        "key": key,
        "value": value
    }
    r = requests.post(f"{SERVER}/sync/set", json=payload)
    return r.json()

def sync_get(key):
    payload = {
        "device_id": DEVICE_ID,
        "key": key
    }
    r = requests.post(f"{SERVER}/sync/get", json=payload)
    return r.json()

# Example usage
print(sync_set("power_level", 9999))
print(sync_get("power_level", 9999))