import json
import datetime
import os

os.makedirs("logs", exist_ok=True)
os.makedirs("security", exist_ok=True)

def log_event(ip="0.0.0.0", event="unknown", path="/"):
    data = {
        "time": str(datetime.datetime.now()),
        "ip": ip,
        "event": event,
        "path": path
    }

    with open("logs/security.log", "a") as f:
        f.write(json.dumps(data) + "\n")

    # also save structured json
    try:
        file = "security/suspicious_ips.json"

        if not os.path.exists(file):
            db = []
        else:
            with open(file) as f:
                db = json.load(f)

        db.append(data)

        with open(file, "w") as f:
            json.dump(db, f, indent=2)

    except:
        pass


if __name__ == "__main__":
    log_event("192.168.1.1", "scan_detected", "/login")
    log_event("10.0.0.5", "failed_login", "/admin")