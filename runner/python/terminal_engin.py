"""Restricted read-only terminal diagnostics; arbitrary shell execution is disabled."""
import shlex
import subprocess

_ALLOWED = {("pwd",), ("whoami",), ("date",), ("python", "--version"), ("python3", "--version"), ("git", "status", "--short")}


def run_terminal_command(command):
    if not isinstance(command, str) or len(command) > 256:
        return {"ok": False, "error": "invalid command"}
    try:
        args = tuple(shlex.split(command))
    except ValueError:
        return {"ok": False, "error": "invalid command syntax"}
    if args not in _ALLOWED:
        return {"ok": False, "error": "command is not in the read-only allowlist"}
    try:
        result = subprocess.run(list(args), shell=False, capture_output=True, text=True, timeout=10)
        return {"ok": result.returncode == 0, "returncode": result.returncode, "output": (result.stdout + result.stderr)[-4000:]}
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"ok": False, "error": type(exc).__name__}


if __name__ == "__main__":
    print(run_terminal_command("python --version"))
