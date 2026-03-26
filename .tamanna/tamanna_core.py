import os
import json
from datetime import datetime

CORE_DIR = ".tamanna_core"
IDENTITY_FILE = "identity.json"

def build_identity():
    return {
        "name": "Tamanna AI",
        "version": "1.0.0",
        "created_at": datetime.utcnow().isoformat() + "Z",
        "author": "HM",
        "description": "Sovereign AI system head & core registry.",
        "tags": [
            "tamanna",
            "sovereign",
            "head",
            "core",
            "hm"
        ]
    }

def main():
    print("🧠 Tamanna CORE: initializing...")

    os.makedirs(CORE_DIR, exist_ok=True)
    identity_path = os.path.join(CORE_DIR, IDENTITY_FILE)

    data = build_identity()

    with open(identity_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"✅ Tamanna CORE written to: {identity_path}")
    print("📦 Identity:", data["name"], "| Version:", data["version"])

if __name__ == "__main__":
    main()
