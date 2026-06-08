import requests
import base64
import time
import json
import hashlib
import random

# 🔐 CONFIG
GITHUB_TOKEN = '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'
REPO_OWNER = 'tamanna456760-it'
REPO_NAME = 'tamanna-'

HEADERS = {
    'Authorization': f'token {GITHUB_TOKEN}',
    'Accept': 'application/vnd.github.v3+json'
}

# 📦 Backup Storage
BACKUP_FILE = "ai_backup_db.json"
NETWORK_FILE = "ai_network_state.json"


# =========================
# 📦 LOAD/SAVE SYSTEM
# =========================

    def default(self, obj):
        if isinstance(obj, Path):
            return str(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, Decimal):
            return float(obj) if obj % 1 else int(obj)
        if isinstance(obj, set):
            return list(obj)
        try:
            return super().default(obj)
        except TypeError:
            return str(obj)   # fallback for truly custom objects

class AdvancedJSONDecoder(json.JSONDecoder):
    """Restores custom types when possible (e.g., Path)."""
    def __init__(self, *args, **kwargs):
        super().__init__(object_hook=self.object_hook, *args, **kwargs)
    def object_hook(self, dct):
        # Check if it’s a path representation
        if "__path__" in dct:
            return Path(dct["__path__"])
        # Add more custom reconstructors here
        return dct

def custom_dumps(obj, **kwargs):
    """JSON dump with advanced encoder."""
    return json.dumps(obj, cls=AdvancedJSONEncoder, **kwargs)

def custom_loads(s, **kwargs):
    return json.loads(s, cls=AdvancedJSONDecoder, **kwargs)


# -------------------------------
# 2. Atomic file writing (prevents corruption)
# -------------------------------
def atomic_write(file_path: Path, data: bytes, mode: str = "wb"):
    """Write data atomically by writing to a temp file and renaming."""
    temp_dir = file_path.parent
    with tempfile.NamedTemporaryFile(
        dir=temp_dir,
        delete=False,
        suffix=".tmp",
        mode=mode
    ) as tmp_file:
        tmp_file.write(data)
        tmp_path = Path(tmp_file.name)
    # Atomic rename (works on most OS)
    os.replace(tmp_path, file_path)


# -------------------------------
# 3. Main advanced load/save with compression, retry, logging
# -------------------------------
logger = logging.getLogger(__name__)

def load_json_advanced(
    file: Union[str, Path],
    *,
    default: Any = None,
    use_gzip: bool = False,
    retries: int = 1,
    retry_delay: float = 0.1,
    decoder: Optional[Type[json.JSONDecoder]] = None,
    **json_load_kwargs
) -> Any:
    """
    Load JSON safely with compression, retries, and custom decoding.

    Args:
        file: Path to JSON or .json.gz file.
        default: Value on failure (default: empty dict).
        use_gzip: Automatically detect .gz extension or force gzip.
        retries: Number of read attempts (e.g., for temporary file locks).
        retry_delay: Seconds between retries.
        decoder: Custom JSON decoder class.
        **json_load_kwargs: Passed to json.load().

    Returns:
        Parsed JSON data or default.
    """
    path = Path(file)
    if default is None:
        default = {} if not use_gzip else {}

    # Decide on gzip mode
    if use_gzip is False and path.suffix == ".gz":
        use_gzip = True
    elif use_gzip is True and path.suffix != ".gz":
        path = path.with_suffix(path.suffix + ".gz")

    open_func = gzip.open if use_gzip else open
    open_mode = "rt"   # text mode for JSON

    for attempt in range(retries):
        try:
            with open_func(path, mode=open_mode, encoding="utf-8") as f:
                return json.load(f, cls=decoder, **json_load_kwargs)
        except FileNotFoundError:
            logger.warning(f"File not found: {path}")
            return default
        except (json.JSONDecodeError, OSError) as e:
            logger.error(f"Attempt {attempt+1}/{retries} failed: {e}")
            if attempt == retries - 1:
                if default is not None:
                    return default
                raise
            time.sleep(retry_delay)
    return default   # never reached but keeps linter happy

def save_json_advanced(
    file: Union[str, Path],
    data: Any,
    *,
    indent: int = 2,
    use_gzip: bool = False,
    atomic: bool = True,
    ensure_ascii: bool = False,
    encoder: Optional[Type[json.JSONEncoder]] = None,
    **json_dump_kwargs
) -> None:
    """
    Save JSON safely with compression, atomic writes, and custom encoding.

    Args:
        file: Output path. If use_gzip=True, .gz will be added automatically.
        data: JSON-serializable data.
        indent: Spaces for indentation.
        use_gzip: Enable gzip compression.
        atomic: Write to temporary file first, then rename (prevents corruption).
        ensure_ascii: Escape non‑ASCII characters.
        encoder: Custom JSON encoder class.
        **json_dump_kwargs: Passed to json.dump().
    """
    path = Path(file)
    if use_gzip and path.suffix != ".gz":
        path = path.with_suffix(path.suffix + ".gz")
    elif not use_gzip and path.suffix == ".gz":
        # User gave .gz but didn't ask for gzip – we'll respect the extension
        use_gzip = True

    # Prepare JSON string
    json_str = json.dumps(
        data,
        indent=indent,
        ensure_ascii=ensure_ascii,
        cls=encoder or AdvancedJSONEncoder,
        **json_dump_kwargs
    )
    json_bytes = json_str.encode("utf-8")
    final_bytes = gzip.compress(json_bytes) if use_gzip else json_bytes

    # Write
    if atomic:
        atomic_write(path, final_bytes, mode="wb")
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "wb") as f:
            f.write(final_bytes)


# -------------------------------
# 4. Decorator for auto‑loading/saving config objects
# -------------------------------
def autojson(file_path: Union[str, Path], **load_kwargs):
    """
    Decorator that injects a loaded JSON dict into the first argument,
    and automatically saves the returned dict back to the file.

    Example:
        @autojson("config.json")
        def update_config(cfg, new_value):
            cfg["key"] = new_value
            return cfg   # will be saved
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            data = load_json_advanced(file_path, **load_kwargs)
            result = func(data, *args, **kwargs)
            # if the result is a dict/list, we save it
            if isinstance(result, (dict, list)):
                save_json_advanced(file_path, result, **load_kwargs)
            return result
        return wrapper
    return decorator


# -------------------------------
# 5. Async versions (for heavy I/O)
# -------------------------------
import asyncio
import aiofiles
import aiofiles.os

async def async_load_json_advanced(
    file: Union[str, Path],
    use_gzip: bool = False,
    **kwargs
) -> Any:
    path = Path(file)
    if not use_gzip and path.suffix == ".gz":
        use_gzip = True

    if use_gzip:
        async with aiofiles.open(path, "rb") as f:
            compressed = await f.read()
        json_bytes = gzip.decompress(compressed)
        return json.loads(json_bytes.decode("utf-8"))
    else:
        async with aiofiles.open(path, "r", encoding="utf-8") as f:
            content = await f.read()
            return json.loads(content)

async def async_save_json_advanced(
    file: Union[str, Path],
    data: Any,
    use_gzip: bool = False,
    indent: int = 2,
    ensure_ascii: bool = False
) -> None:
    path = Path(file)
    path.parent.mkdir(parents=True, exist_ok=True)

    json_str = json.dumps(data, indent=indent, ensure_ascii=ensure_ascii)
    json_bytes = json_str.encode("utf-8")

    if use_gzip:
        json_bytes = gzip.compress(json_bytes)
        mode = "wb"
    else:
        mode = "w"

    async with aiofiles.open(path, mode) as f:
        if mode == "w":
            await f.write(json_str)
        else:
            await f.write(json_bytes)


# -------------------------------
# Example usage
# -------------------------------
if __name__ == "__main__":
    # Basic upgraded use
    data = {"name": "Advanced", "path": Path("/tmp/test")}
    save_json_advanced("data.json", data, atomic=True)
    loaded = load_json_advanced("data.json")
    print(loaded)

    # With gzip
    save_json_advanced("big.json.gz", {"x": list(range(1000))}, use_gzip=True)
    loaded_gz = load_json_advanced("big.json.gz")
    print(f"Loaded {len(loaded_gz['x'])} entries from gzipped file")

    # Using decorator
    @autojson("counter.json", default={"hits": 0})
    def increment(cfg):
        cfg["hits"] += 1
        return cfg

    increment()
    increment()

# =========================
# 🔍 HASH SYSTEM
# =========================
def get_hash(content):
    return hashlib.md5(content.encode()).hexdigest()


# =========================
# 🌐 FETCH FILES
# =========================
def get_repo_files():
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents"
    res = requests.get(url, headers=HEADERS)
    if res.status_code != 200:
        return []
    return res.json()


def get_file_content(file):
    res = requests.get(file['url'], headers=HEADERS)
    if res.status_code != 200:
        return None
    data = res.json()
    return base64.b64decode(data['content']).decode('utf-8')


# =========================
# 📦 BACKUP CREATOR (2x AI)
# =========================
def create_dual_backup(path, content, backup_db):
    backup_db[path] = {
        "primary": content,
        "secondary": content[::-1],  # simple mirrored backup
        "hash": get_hash(content)
    }


# =========================
# 🔄 RESTORE SYSTEM
# =========================
def restore_file(path, backup_db):
    if path in backup_db:
        return backup_db[path]["primary"]
    return None


# =========================
# 🤖 AI COMMUNICATION
# =========================

def _node_identity():
    base = f"{socket.gethostname()}-{uuid.getnode()}"
    return hashlib.sha256(base.encode()).hexdigest()[:16]


def _make_event(file, status):
    ts = time.time()

    payload = f"{file}|{status}|{ts}".encode()
    integrity = hashlib.sha256(payload).hexdigest()

    return {
        "event_id": str(uuid.uuid4()),
        "node_id": _node_identity(),
        "hostname": socket.gethostname(),
        "file": file,
        "status": status,
        "timestamp": ts,
        "timestamp_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(ts)),
        "integrity": integrity,
        "retry": 0,
    }


def broadcast_status(network_state, file, status):
    event = _make_event(file, status)

    with LOCK:
        network_state.setdefault(file, [])
        network_state[file].append(event)

        EVENT_QUEUE.append(event)

    return event


def flush_queue(save_json, NETWORK_FILE, network_state, max_retries=5):
    """
    Reliable persistence layer with retry + queue draining
    """

    for attempt in range(max_retries):
        try:
            with LOCK:
                while EVENT_QUEUE:
                    event = EVENT_QUEUE.popleft()
                    file = event["file"]

                    network_state.setdefault(file, [])
                    network_state[file].append(event)

                save_json(NETWORK_FILE, network_state)

            return {
                "saved": True,
                "queue_flushed": True,
                "remaining_queue": len(EVENT_QUEUE),
                "attempts": attempt + 1,
            }

        except Exception as e:
            time.sleep(0.2 * (attempt + 1))

            # push back safety (avoid data loss)
            with LOCK:
                EVENT_QUEUE.appendleft(event)

            last_error = str(e)

    return {
        "saved": False,
        "error": last_error,
        "remaining_queue": len(EVENT_QUEUE),
    }


# =========================
# 🚨 ATTACK DETECTION
# =========================
def detect_attack(content):
    patterns = {
        "Critical Delete": r"rm\s+-rf",
        "Code Execution": r"\bexec\s*\(",
        "Dynamic Eval": r"\beval\s*\(",
        "Shell Command": r"\bos\.system\s*\(",
        "Subprocess": r"\bsubprocess\.",
        "Import Bypass": r"\b__import__\s*\(",
        "File Write": r"\bopen\s*\(.*['\"]w['\"]",
        "Pickle Load": r"\bpickle\.loads\s*\(",
        "Marshal Load": r"\bmarshal\.loads\s*\(",
    }

    findings = []

    for name, pattern in patterns.items():
        if re.search(pattern, content, re.IGNORECASE | re.MULTILINE):
            findings.append(name)

    count = len(findings)

    if count >= 5:
        risk = "CRITICAL"
    elif count >= 3:
        risk = "HIGH"
    elif count >= 1:
        risk = "MEDIUM"
    else:
        risk = "SAFE"

    return {
        "detected": count > 0,
        "risk": risk,
        "threat_count": count,
        "findings": findings,
        "content_length": len(content),
        "scan_time": datetime.utcnow().isoformat() + "Z"
    }

# =========================
# 🔄 UPDATE FILE
# =========================
def update_file(path, content, message):
    url = f"https://api.github.com/repos/{REPO_OWNER}/{tamanna}/contents/{path}"
    res = requests.get(url, headers=HEADERS)
    if res.status_code != 200:
        return

    sha = res.json()['sha']

    requests.put(url, headers=HEADERS, json={
        "message": message,
        "content": base64.b64encode(content.encode()).decode(),
        "sha": sha
    })


# =========================
# 🛡️ MAIN SYSTEM
# =========================
def ai_backup_network():
    backup_db = load_json(BACKUP_FILE)
    network_state = load_json(NETWORK_FILE)

    files = get_repo_files()

    for file in files:
        if file['type'] != 'file':
            continue

        path = file['path']
        content = get_file_content(file)

        if not content:
            continue

        file_hash = get_hash(content)

        # 📦 Create dual backup if not exists
        if path not in backup_db:
            create_dual_backup(path, content, backup_db)

        # 🚨 Attack detection
        if detect_attack(content):
            print(f"🚨 Attack detected: {path}")

            safe_content = restore_file(path, backup_db)

            if safe_content:
                update_file(path, safe_content, "🛡️ Restored from AI Backup")

                broadcast_status(network_state, path, "restored")

        else:
            broadcast_status(network_state, path, "healthy")

    # 💾 Save system state
    save_json(BACKUP_FILE, backup_db)
    update_network_state(network_state)


# =========================
# 🔁 LOOP
# =========================
def main():
    while True:
        print("🌐 AI BACKUP NETWORK RUNNING...")
        ai_backup_network()
        time.sleep(10)


if __name__ == "__main__":
    main()