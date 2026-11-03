"""Read-only security scanner; automatic GitHub restoration is intentionally disabled."""
import hashlib
import os
import requests

OWNER = "tamanna456760-it"
REPO = "Tamanna-"
API = f"https://api.github.com/repos/{OWNER}/{REPO}"
TIMEOUT = (5, 20)
MAX_BYTES = 2 * 1024 * 1024
DANGEROUS_KEYWORDS = ("os.system", "rm -rf", "eval(", "exec(", "chmod 777", "shell=True")


def _headers():
    headers = {"Accept": "application/vnd.github+json"}
    token = os.getenv("TAMANNA_GITHUB_TOKEN", "").strip()
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def generate_hash(content):
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def is_dangerous(code):
    return any(term in code for term in DANGEROUS_KEYWORDS)


def scan_and_protect():
    """Return a read-only report for the default branch; never modifies repository files."""
    response = requests.get(f"{API}/git/trees/main?recursive=1", headers=_headers(), timeout=TIMEOUT)
    response.raise_for_status()
    tree = response.json()
    if tree.get("truncated"):
        raise RuntimeError("Git tree is truncated; scan is incomplete.")
    report = []
    for item in tree.get("tree", []):
        if item.get("type") != "blob" or item.get("size", MAX_BYTES + 1) > MAX_BYTES:
            continue
        path = item.get("path", "")
        if any(part in {".git", ".venv", "venv", "node_modules", "__pycache__"} for part in path.split("/")):
            continue
        report.append({"file": path, "status": "review_required" if is_dangerous(path) else "not_scanned", "sha": item.get("sha")})
    return {"mode": "read_only", "files_listed": len(report), "report": report, "automatic_restore": False, "github_write_enabled": False}


if __name__ == "__main__":
    print(scan_and_protect())
