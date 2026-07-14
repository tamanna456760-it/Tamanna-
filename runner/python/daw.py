#!/usr/bin/env python3

import hashlib
import json
import os
import time
from datetime import datetime

SYSTEM = "BD-KING-R7"
MODULES = "modules"
MANIFEST = "hash_manifest.json"
MYTH = "myth_log.jsonl"


def now():
    return datetime.utcnow().isoformat() + "Z"


def log(event, data):
    with open(MYTH, "a", encoding="utf-8") as f:
        f.write(json.dumps({"time": now(), "event": event, "data": data}) + "\n")


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def build_manifest():
    m = {}
    for root, _, files in os.walk(MODULES):
        for name in files:
            p = os.path.join(root, name)
            r = os.path.relpath(p, MODULES)
            m[r] = sha256(p)
    return m


def save_manifest(m):
    with open(MANIFEST, "w") as f:
        json.dump(m, f, indent=2)


def init_integrity():
    m = build_manifest()
    save_manifest(m)
    log("integrity_init", {"files": len(m)})
    print("Manifest initialized.")


def check_integrity():
    if not os.path.exists(MANIFEST):
        print("No manifest. Run init_integrity() first.")
        return

    stored = json.load(open(MANIFEST))
    current = build_manifest()

    added = set(current) - set(stored)
    removed = set(stored) - set(current)
    changed = {f for f in stored if f in current and stored[f] != current[f]}

    if not added and not removed and not changed:
        print("Integrity OK.")
        log("integrity_ok", {})
        return

    print("Integrity deviation detected.")
    log(
        "integrity_violation",
        {"added": list(added), "removed": list(removed), "changed": list(changed)},
    )


def heartbeat():
    print(f"{SYSTEM} heartbeat at {now()}")
    log("heartbeat", {"alive": True})


def run():
    print(f"{SYSTEM} security engine started.")
    last_hb = 0
    last_chk = 0

    while True:
        t = time.time()

        if t - last_hb >= 5:
            heartbeat()
            last_hb = t

        if t - last_chk >= 10:
            check_integrity()
            last_chk = t

        time.sleep(1)


if __name__ == "__main__":
    run()
