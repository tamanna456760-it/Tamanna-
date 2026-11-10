#!/usr/bin/env python3
"""Small connectivity check using a fixed host and shell-free subprocess."""
import subprocess

HOST = "google.com"


def main():
    try:
        result = subprocess.run(
            ["ping", "-c", "1", HOST],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=5,
        )
    except FileNotFoundError:
        print("Ping utility is not installed")
        return 127
    except subprocess.TimeoutExpired:
        print("Ping timed out")
        return 124

    if result.returncode == 0:
        print("Ping OK")
        return 0
    print("Ping failed")
    return result.returncode or 1


if __name__ == "__main__":
    raise SystemExit(main())
