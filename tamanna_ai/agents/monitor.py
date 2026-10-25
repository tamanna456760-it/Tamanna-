"""Tamanna AI Monitor Agent."""
import os
import shutil
from pathlib import Path
from typing import Optional
class MonitorAgent:
    def check_path(self, path: str) -> dict:
        target = Path(path)
        return {
            "path": str(target),
            "exists": target.exists(),
            "is_file": target.is_file(),
            "is_directory": target.is_dir(),
            "readable": os.access(target, os.R_OK) if target.exists() else False,
            "writable": os.access(target, os.W_OK) if target.exists() else False,
        }
    def check_disk(self, path: str = ".") -> dict:
        target = Path(path).resolve()
        if not target.exists():
            return {
                "success": False,
                "error": "Path does not exist.",
            }
        try:
            usage = shutil.disk_usage(target)
            return {
                "success": True,
                "path": str(target),
                "total_bytes": usage.total,
                "used_bytes": usage.used,
                "free_bytes": usage.free,
                "free_percent": round(usage.free / usage.total * 100, 2)
                if usage.total else 0,
            }
        except OSError as exc:
            return {"success": False, "error": str(exc)}
    def check_http(self, url: str, timeout: float = 5.0) -> dict:
        """Check an HTTP endpoint using only Python's standard library."""
        import urllib.error
        import urllib.request
        if not url.startswith(("https://", "http://")):
            return {"success": False, "error": "Only HTTP/HTTPS URLs are supported."}
        if not 0.1 <= timeout <= 30:
            return {"success": False, "error": "Timeout must be between 0.1 and 30 seconds."}
        request = urllib.request.Request(
            url,
            method="GET",
            headers={"User-Agent": "Tamanna-Monitor/1.0"},
        )
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                return {
                    "success": 200 <= response.status < 400,
                    "status_code": response.status,
                    "url": url,
                }
        except urllib.error.HTTPError as exc:
            return {
                "success": False,
                "status_code": exc.code,
                "url": url,
            }
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            return {
                "success": False,
                "url": url,
                "error": str(exc),
            }
if __name__ == "__main__":
    agent = MonitorAgent()
    print(agent.check_disk("."))