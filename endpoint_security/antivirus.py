"""Optional ClamAV-backed malware scanning for Tamanna AI.

This is a defensive, read-only scanner. It never executes, deletes, or
quarantines scanned files. Install ClamAV separately to enable scanning.
"""
from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from typing import Any


class AntivirusScanner:
    """Scan regular files with the locally installed ClamAV clamscan binary."""

    def __init__(
        self,
        timeout_seconds: int = 60,
        max_file_size_bytes: int = 100 * 1024 * 1024,
    ) -> None:
        if timeout_seconds < 1:
            raise ValueError("timeout_seconds must be positive")
        if max_file_size_bytes < 0:
            raise ValueError("max_file_size_bytes cannot be negative")
        self.timeout_seconds = timeout_seconds
        self.max_file_size_bytes = max_file_size_bytes

    def scan_file(self, file_path: str | Path) -> dict[str, Any]:
        """Return a structured scan result; no file contents are modified."""
        path = Path(file_path)
        try:
            if path.is_symlink():
                return self._result("skipped", path, "symbolic links are not followed")
            resolved = path.resolve(strict=True)
            if not resolved.is_file():
                return self._result("error", resolved, "not a regular file")
            size = resolved.stat().st_size
            if size > self.max_file_size_bytes:
                return self._result(
                    "skipped", resolved, "file exceeds configured size limit",
                    size_bytes=size,
                )
        except OSError as exc:
            return self._result("error", path, str(exc))

        binary = shutil.which("clamscan")
        if not binary:
            return self._result(
                "engine_unavailable", resolved,
                "ClamAV clamscan was not found; install ClamAV and update signatures",
                size_bytes=size,
            )

        try:
            completed = subprocess.run(
                [binary, "--no-summary", str(resolved)],
                capture_output=True,
                text=True,
                timeout=self.timeout_seconds,
                check=False,
            )
        except subprocess.TimeoutExpired:
            return self._result("error", resolved, "scan timed out", size_bytes=size)
        except OSError as exc:
            return self._result("error", resolved, str(exc), size_bytes=size)

        output = "\n".join(part for part in (completed.stdout, completed.stderr) if part)
        if completed.returncode == 0:
            return self._result("clean", resolved, "no malware detected by ClamAV", size_bytes=size)
        if completed.returncode == 1:
            signature = next(
                (line.rsplit(": ", 1)[-1][:-6] for line in output.splitlines()
                 if line.endswith(" FOUND")),
                "Malware signature detected",
            )
            return self._result(
                "infected", resolved, signature, size_bytes=size,
                engine="ClamAV",
            )
        return self._result(
            "error", resolved, "ClamAV scan failed",
            size_bytes=size, engine_exit_code=completed.returncode,
        )

    @staticmethod
    def _result(
        status: str,
        path: Path,
        message: str,
        **extra: Any,
    ) -> dict[str, Any]:
        return {
            "scanner": "Tamanna AI Antivirus",
            "status": status,
            "path": str(path),
            "message": message,
            **extra,
        }
