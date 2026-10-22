"""File integrity inspection for Tamanna AI Endpoint Security.
Owner: HM INSAN ALI
This module calculates SHA-256 hashes for explicitly configured files.
It does not modify, quarantine, or delete files.
"""
from __future__ import annotations
import hashlib
from pathlib import Path
from typing import Any
class FileIntegrityMonitor:
    """Calculate hashes and compare them with a supplied baseline."""
    def __init__(self, config: dict[str, Any]):
        self.config = config or {}
        self.settings = self.config.get("file_integrity", {})
        if self.settings.get("hash_algorithm", "sha256") != "sha256":
            raise ValueError("Only SHA-256 is supported")
        self.max_file_size = int(
            self.settings.get("max_file_size_bytes", 10 * 1024 * 1024)
        )
        if self.max_file_size < 0:
            raise ValueError("max_file_size_bytes cannot be negative")
    def hash_file(self, file_path: str | Path) -> dict[str, Any]:
        """Return the SHA-256 hash of a file without changing it."""
        path = Path(file_path)
        try:
            if path.is_symlink() and not self.settings.get(
                "follow_symlinks", False
            ):
                return {
                    "status": "skipped",
                    "path": str(path),
                    "reason": "symbolic links are not followed",
                }
            if not path.is_file():
                return {
                    "status": "error",
                    "path": str(path),
                    "reason": "not a regular file",
                }
            size = path.stat().st_size
            if size > self.max_file_size:
                return {
                    "status": "skipped",
                    "path": str(path),
                    "size_bytes": size,
                    "reason": "file exceeds configured size limit",
                }
            digest = hashlib.sha256()
            with path.open("rb") as file_handle:
                for chunk in iter(lambda: file_handle.read(65536), b""):
                    digest.update(chunk)
            return {
                "status": "ok",
                "path": str(path),
                "size_bytes": size,
                "sha256": digest.hexdigest(),
            }
        except OSError as exc:
            return {
                "status": "error",
                "path": str(path),
                "reason": str(exc),
            }
    def compare(
        self,
        file_path: str | Path,
        baseline_sha256: str,
    ) -> dict[str, Any]:
        """Compare a file's current hash with a supplied trusted baseline."""
        if (
            not isinstance(baseline_sha256, str)
            or len(baseline_sha256) != 64
            or any(char not in "0123456789abcdefABCDEF"
                   for char in baseline_sha256)
        ):
            return {
                "status": "error",
                "path": str(file_path),
                "reason": "invalid SHA-256 baseline",
            }
        current = self.hash_file(file_path)
        if current["status"] != "ok":
            return current
        changed = current["sha256"].lower() != baseline_sha256.lower()
        return {
            "status": "changed" if changed else "unchanged",
            "path": current["path"],
            "size_bytes": current["size_bytes"],
            "sha256": current["sha256"],
        }