import base64
import hashlib
import json
import logging
import os
import sys
import time
from dataclasses import dataclass
from functools import wraps
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import requests
from dotenv import load_dotenv  # pip install python-dotenv

load_dotenv()  # Load token from .env file (never hardcode!)

# -------------------------------
# 1. Secure configuration
# -------------------------------
@dataclass
class GitHubConfig:
    token: str
    owner: str
    repo: str
    base_url: str = "https://api.github.com"
    per_page: int = 30
    max_retries: int = 3
    retry_delay: float = 1.0

    @classmethod
    def from_env(cls):
        """Load from environment variables (safe for production)."""
        token = os.getenv("GITHUB_TOKEN")
        if not token:
            raise ValueError("GITHUB_TOKEN not set in environment")
        owner = os.getenv("REPO_OWNER")
        repo = os.getenv("REPO_NAME")
        if not owner or not repo:
            raise ValueError("REPO_OWNER and REPO_NAME must be set")
        return cls(token=token, owner=owner, repo=repo)


# -------------------------------
# 2. Logging setup
# -------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("github_client")


# -------------------------------
# 3. Exception classes
# -------------------------------
class GitHubAPIError(Exception):
    """Raised when GitHub API returns an error."""
    pass

class RateLimitExceeded(GitHubAPIError):
    pass


# -------------------------------
# 4. Advanced GitHub client
# -------------------------------
class GitHubClient:
    def __init__(self, config: GitHubConfig):
        self.config = config
        self.session = self._create_session()

    def _create_session(self) -> requests.Session:
        session = requests.Session()
        session.headers.update({
            "Authorization": f"token {self.config.token}",
            "Accept": "application/vnd.github.v3+json"
        })
        return session

    def _handle_rate_limit(self, response: requests.Response) -> None:
        """Check rate limit and raise if exhausted."""
        remaining = int(response.headers.get("X-RateLimit-Remaining", 1))
        if remaining == 0:
            reset_time = int(response.headers.get("X-RateLimit-Reset", 0))
            sleep_seconds = max(0, reset_time - time.time()) + 1
            logger.warning(f"Rate limit hit. Sleeping {sleep_seconds:.0f}s")
            time.sleep(sleep_seconds)

    def _request(
        self,
        method: str,
        endpoint: str,
        retry_count: int = 0,
        **kwargs
    ) -> requests.Response:
        url = f"{self.config.base_url}/{endpoint.lstrip('/')}"
        try:
            resp = self.session.request(method, url, **kwargs)
            self._handle_rate_limit(resp)

            if resp.status_code == 404:
                return resp   # not an error, just not found
            if resp.status_code >= 400:
                # Try to parse error message
                try:
                    error_data = resp.json()
                    msg = error_data.get("message", resp.text)
                except:
                    msg = resp.text
                raise GitHubAPIError(f"GitHub API error {resp.status_code}: {msg}")

            return resp

        except (requests.ConnectionError, requests.Timeout) as e:
            logger.error(f"Network error: {e}")
            if retry_count < self.config.max_retries:
                time.sleep(self.config.retry_delay * (2 ** retry_count))
                return self._request(method, endpoint, retry_count + 1, **kwargs)
            raise

    def get_paginated(self, endpoint: str, **kwargs) -> List[Dict]:
        """Handle pagination automatically (supports link header)."""
        results = []
        url = f"{self.config.base_url}/{endpoint.lstrip('/')}"
        params = kwargs.pop("params", {})
        params["per_page"] = self.config.per_page
        page = 1

        while True:
            params["page"] = page
            resp = self.session.get(url, params=params, **kwargs)
            self._handle_rate_limit(resp)
            if resp.status_code != 200:
                break
            data = resp.json()
            if not data:
                break
            results.extend(data)
            page += 1
        return results

    # ---------------------------
    # Repository operations
    # ---------------------------
    def get_file_content(self, file_path: str, branch: str = "main") -> Optional[str]:
        """Get raw content of a file as string (decoded from base64)."""
        endpoint = f"repos/{self.config.owner}/{self.config.repo}/contents/{file_path}"
        params = {"ref": branch}
        try:
            resp = self._request("GET", endpoint, params=params)
            if resp.status_code == 404:
                return None
            data = resp.json()
            content = data.get("content", "")
            if content:
                return base64.b64decode(content).decode("utf-8")
        except GitHubAPIError as e:
            logger.error(f"Failed to get file {file_path}: {e}")
        return None

    def create_or_update_file(
        self,
        file_path: str,
        content: str,
        commit_message: str,
        branch: str = "main",
        sha: Optional[str] = None
    ) -> Dict:
        """
        Create or update a file in the repo.
        If sha is None, it will try to fetch existing sha first.
        """
        # If sha not provided, try to fetch existing file
        if sha is None:
            existing = self.get_file_metadata(file_path, branch)
            if existing:
                sha = existing.get("sha")

        endpoint = f"repos/{self.config.owner}/{self.config.repo}/contents/{file_path}"
        data = {
            "message": commit_message,
            "content": base64.b64encode(content.encode("utf-8")).decode("utf-8"),
            "branch": branch
        }
        if sha:
            data["sha"] = sha

        resp = self._request("PUT", endpoint, json=data)
        return resp.json()

    def get_file_metadata(self, file_path: str, branch: str = "main") -> Optional[Dict]:
        """Get file metadata (including sha) without downloading content."""
        endpoint = f"repos/{self.config.owner}/{self.config.repo}/contents/{file_path}"
        params = {"ref": branch}
        try:
            resp = self._request("GET", endpoint, params=params)
            if resp.status_code == 404:
                return None
            return resp.json()
        except GitHubAPIError:
            return None

    def delete_file(self, file_path: str, commit_message: str, branch: str = "main") -> bool:
        """Delete a file from the repo."""
        metadata = self.get_file_metadata(file_path, branch)
        if not metadata:
            logger.warning(f"File {file_path} does not exist")
            return False

        endpoint = f"repos/{self.config.owner}/{self.config.repo}/contents/{file_path}"
        data = {
            "message": commit_message,
            "sha": metadata["sha"],
            "branch": branch
        }
        self._request("DELETE", endpoint, json=data)
        return True

    def get_all_files_in_path(self, path: str = "", branch: str = "main") -> List[Dict]:
        """Recursively get all files in a directory."""
        endpoint = f"repos/{self.config.owner}/{self.config.repo}/contents/{path}"
        params = {"ref": branch}
        resp = self._request("GET", endpoint, params=params)
        items = resp.json()
        files = []
        for item in items:
            if item["type"] == "file":
                files.append(item)
            elif item["type"] == "dir":
                files.extend(self.get_all_files_in_path(item["path"], branch))
        return files

    # ---------------------------
    # Utility: commit hash & tree
    # ---------------------------
    def get_last_commit_sha(self, branch: str = "main") -> Optional[str]:
        endpoint = f"repos/{self.config.owner}/{self.config.repo}/git/ref/heads/{branch}"
        try:
            resp = self._request("GET", endpoint)
            return resp.json()["object"]["sha"]
        except GitHubAPIError:
            return None


# -------------------------------
# 5. Decorator for automatic retry & rate limit handling
# -------------------------------
def github_retry(max_attempts=3):
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(self, *args, **kwargs)
                except (requests.ConnectionError, RateLimitExceeded) as e:
                    if attempt == max_attempts - 1:
                        raise
                    wait = 2 ** attempt
                    logger.warning(f"Retry {attempt+1} after {wait}s: {e}")
                    time.sleep(wait)
                except GitHubAPIError as e:
                    # Do not retry on 4xx client errors (except 429)
                    if "429" in str(e):
                        continue
                    raise
            return None
        return wrapper
    return decorator


# -------------------------------
# Example usage (production ready)
# -------------------------------
if __name__ == "__main__":
    # Initialize from environment (safe)
    config = GitHubConfig.from_env()
    client = GitHubClient(config)

    # Example: Read a file
    content = client.get_file_content("README.md")
    print(f"README.md exists: {content is not None}")

    # Example: Create/update a JSON file
    data = {"timestamp": time.time(), "value": random.randint(1, 100)}
    json_str = json.dumps(data, indent=2)
    result = client.create_or_update_file(
        "data/config.json",
        json_str,
        "Update config via script"
    )
    print(f"File updated: {result['content']['sha']}")

    # Example: Delete a file
    # client.delete_file("data/old.json", "Remove old file")

    # Example: Get all Python files in src/
    # py_files = client.get_all_files_in_path("src", branch="main")
    # for f in py_files:
    #     print(f['path'])

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

def signal_handler(signum, frame):
    """Handle SIGINT (Ctrl+C) and SIGTERM."""
    global shutdown_requested
    logger.info(f"Received signal {signum}, shutting down gracefully...")
    shutdown_requested = True

def ai_backup_network():
    """
    Your actual backup logic (mock here, replace with your real function).
    Should raise exceptions on failure.
    """
    # Simulate work – replace with real GitHub / backup operations
    logger.info("Running AI backup network cycle...")
    # Example: call your GitHub sync function
    # from github_client import GitHubClient, GitHubConfig
    # config = GitHubConfig.from_env()
    # client = GitHubClient(config)
    # client.backup_all_repos()
    time.sleep(2)   # placeholder for real work
    logger.info("Backup cycle completed successfully.")

def run_forever(
    interval_seconds: int,
    on_failure: Optional[Callable[[Exception], None]] = None,
    max_failures_before_sleep: int = 3
):
    """Main loop with exponential backoff on failures."""
    global shutdown_requested
    consecutive_failures = 0
    current_interval = interval_seconds

    logger.info(f"AI Backup Network started. Interval: {interval_seconds}s")

    while not shutdown_requested:
        try:
            ai_backup_network()
            # Success – reset failure counter and interval
            consecutive_failures = 0
            current_interval = interval_seconds
        except Exception as e:
            logger.exception(f"Backup cycle failed: {e}")
            consecutive_failures += 1
            if on_failure:
                on_failure(e)

            # Exponential backoff on repeated failures
            if consecutive_failures >= max_failures_before_sleep:
                backoff = min(300, current_interval * 2)  # max 5 minutes
                logger.warning(f"Pausing for {backoff}s due to repeated failures")
                current_interval = backoff
            else:
                current_interval = interval_seconds

        # Wait for next cycle, but break early if shutdown requested
        for _ in range(current_interval):
            if shutdown_requested:
                break
            time.sleep(1)

    logger.info("Shutdown complete. Goodbye.")

def parse_args():
    parser = argparse.ArgumentParser(
        description="AI Backup Network Service",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "-i", "--interval",
        type=int,
        default=int(os.getenv("BACKUP_INTERVAL", "60")),
        help="Seconds between backup cycles"
    )
    parser.add_argument(
        "--max-failures",
        type=int,
        default=3,
        help="Consecutive failures before increasing interval"
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Run a single cycle then exit"
    )
    return parser.parse_args()

def main():
    args = parse_args()

    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    if args.once:
        try:
            ai_backup_network()
            logger.info("Single backup cycle finished successfully.")
        except Exception as e:
            logger.exception("Backup cycle failed")
            sys.exit(1)
    else:
        run_forever(
            interval_seconds=args.interval,
            max_failures_before_sleep=args.max_failures,
            on_failure=lambda e: logger.error(f"Failure callback: {e}")
        )

if __name__ == "__main__":
    main()