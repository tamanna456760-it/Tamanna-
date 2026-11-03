"""Read-only defense helpers. No automatic restore or remote writes are permitted."""
import hashlib
import json
from pathlib import Path

DANGEROUS_PATTERNS = ("os.system", "rm -rf", "eval(", "exec(", "chmod 777", "requests.post(", "pickle.loads")
AI_MEMORY_FILE = Path("ai_memory.json")


def get_hash(content):
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def detect_threat(code):
    return [pattern for pattern in DANGEROUS_PATTERNS if pattern in code]


def load_memory():
    try:
        data = json.loads(AI_MEMORY_FILE.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def save_memory(data):
    AI_MEMORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    AI_MEMORY_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")


def defense_engine():
    """Explicitly local, read-only helper; remote repository mutation is disabled."""
    return {"mode": "read_only", "status": "idle", "automatic_restore": False, "github_write_enabled": False}


def main():
    print(json.dumps(defense_engine()))


if __name__ == "__main__":
    main()
