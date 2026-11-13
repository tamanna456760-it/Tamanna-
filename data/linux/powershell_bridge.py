"""Restricted PowerShell diagnostics bridge for Tamanna AI.

Uses pwsh only when installed. Accepts a small read-only command allowlist;
file mutations go through the separately confined workspace API.
"""
from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MAX_TIMEOUT = 20
MAX_OUTPUT = 12_000


class PowerShellBridge:
    def __init__(self, root: str | Path = ROOT):
        self.root = Path(root).resolve()
        self.executable = shutil.which("pwsh")

    def _build(self, command: str) -> str:
        if not isinstance(command, str) or not command.strip() or len(command) > 1000:
            raise ValueError("Provide a PowerShell command up to 1000 characters.")
        if any(ord(ch) < 32 and ch not in "\t" for ch in command):
            raise ValueError("Control characters are not allowed.")
        # Never pass user text as an arbitrary PowerShell program.
        if command.strip() in {"Get-Location", "Get-Date", "$PSVersionTable.PSVersion", "Get-Process"}:
            return command.strip()
        match = re.fullmatch(r"(Get-ChildItem|Get-Content)\s+(['\"]?)([A-Za-z0-9_./ -]+)\2", command.strip(), re.I)
        if not match:
            raise ValueError(
                "Allowed: Get-Location, Get-Date, $PSVersionTable.PSVersion, Get-Process, "
                "Get-ChildItem <project-relative-path>, Get-Content <project-relative-file>."
            )
        verb, _, relative = match.groups()
        candidate = (self.root / relative.strip()).resolve()
        try:
            candidate.relative_to(self.root)
        except ValueError as exc:
            raise ValueError("Path escapes the project workspace.") from exc
        if any(part == ".git" or part == ".env" or part.startswith(".env.") for part in candidate.relative_to(self.root).parts):
            raise ValueError("Protected path cannot be accessed.")
        if not candidate.exists():
            raise ValueError("Path does not exist.")
        if verb.lower() == "get-content" and (not candidate.is_file() or candidate.stat().st_size > 512_000):
            raise ValueError("Get-Content requires a text file no larger than 512 KB.")
        # Quote the validated absolute path as a PowerShell single-quoted literal.
        safe_path = str(candidate).replace("'", "''")
        return f"{verb} -LiteralPath '{safe_path}'"

    def run(self, command: str, timeout: int = 10) -> dict:
        if isinstance(timeout, bool) or not isinstance(timeout, int) or not 1 <= timeout <= MAX_TIMEOUT:
            return {"ok": False, "error": f"timeout must be between 1 and {MAX_TIMEOUT} seconds"}
        if not self.executable:
            return {"ok": False, "available": False, "error": "PowerShell 7 (pwsh) is not installed on this host."}
        try:
            safe_command = self._build(command)
        except ValueError as exc:
            return {"ok": False, "error": str(exc)}
        try:
            result = subprocess.run(
                [self.executable, "-NoLogo", "-NoProfile", "-NonInteractive", "-Command", safe_command],
                cwd=self.root, shell=False, capture_output=True, text=True,
                timeout=timeout, check=False,
            )
            return {
                "ok": result.returncode == 0, "available": True,
                "command": command, "returncode": result.returncode,
                "stdout": result.stdout[-MAX_OUTPUT:], "stderr": result.stderr[-MAX_OUTPUT:],
            }
        except subprocess.TimeoutExpired:
            return {"ok": False, "available": True, "error": "PowerShell command timed out"}
        except OSError as exc:
            return {"ok": False, "available": True, "error": f"PowerShell could not start: {type(exc).__name__}"}


powershell_bridge = PowerShellBridge()
__all__ = ["PowerShellBridge", "powershell_bridge"]
