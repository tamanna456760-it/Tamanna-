# device_binding.py — run in VS Code
import os, hashlib, json, platform, uuid

def device_fingerprint():
    base = f"{platform.system()}|{platform.machine()}|{uuid.getnode()}"
    return hashlib.sha256(base.encode()).hexdigest()

def seal_payload(payload: dict, secret: str):
    fp = device_fingerprint()
    data = json.dumps(payload, sort_keys=True)
    sig = hashlib.sha256((fp + secret + data).encode()).hexdigest()
    return {"payload": payload, "fingerprint": fp, "signature": sig}

def verify_seal(sealed: dict, secret: str):
    fp = device_fingerprint()
    if fp != sealed["fingerprint"]:
        return False
    data = json.dumps(sealed["payload"], sort_keys=True)
    sig = hashlib.sha256((fp + secret + data).encode()).hexdigest()
    return sig == sealed["signature"]

if __name__ == "__main__":
    secret = os.environ.get("LOCAL_SECRET", "change-me")
    sealed = seal_payload({"user": "hm", "level": 7}, secret)
    print("Sealed:", sealed)
    print("Valid here:", verify_seal(sealed, secret))
