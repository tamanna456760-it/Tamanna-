"""Read-only integrity monitor. It never injects host data or writes repository files."""
import hashlib
import os
import requests

OWNER = "tamanna456760-it"
REPO = "Tamanna-"
API = f"https://api.github.com/repos/{OWNER}/{REPO}"
TIMEOUT = (5, 20)


def _headers():
    headers = {"Accept": "application/vnd.github+json"}
    token = os.getenv("TAMANNA_GITHUB_TOKEN", "").strip()
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def scan_and_update_repo():
    response = requests.get(f"{API}/git/trees/main?recursive=1", headers=_headers(), timeout=TIMEOUT)
    response.raise_for_status()
    data = response.json()
    if data.get("truncated"):
        raise RuntimeError("Git tree response truncated; refusing partial integrity report.")
    return {
        "mode": "read_only",
        "files_listed": sum(1 for item in data.get("tree", []) if item.get("type") == "blob"),
        "tree_sha": data.get("sha"),
        "automatic_ip_mac_injection": False,
        "github_write_enabled": False,
    }


if __name__ == "__main__":
    print(scan_and_update_repo())
