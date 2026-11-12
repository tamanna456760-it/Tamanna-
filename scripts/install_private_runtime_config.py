#!/usr/bin/env python3
"""Install a validated non-secret TI-SERVER runtime config for the backend."""
from __future__ import annotations

import argparse
import os
import tempfile
from pathlib import Path

from tamanna_ai.private_runtime_config import load_private_runtime_config

ROOT = Path(__file__).resolve().parents[1]


def install(source: Path, destination: Path, *, force: bool = False) -> None:
    source = source.expanduser()
    destination = destination.expanduser()
    # Validate the source before copying; the loader never prints config values.
    load_private_runtime_config(source)
    if destination.is_symlink():
        raise ValueError("Refusing to replace a symlink destination.")
    if destination.exists() and not force:
        raise FileExistsError("Destination already exists; pass --force to replace it.")
    destination.parent.mkdir(parents=True, exist_ok=True)
    payload = source.read_bytes()
    fd, temporary_name = tempfile.mkstemp(prefix=".private-runtime-", dir=str(destination.parent))
    temporary = Path(temporary_name)
    try:
        os.fchmod(fd, 0o600)
        with os.fdopen(fd, "wb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        if destination.exists() and not force:
            raise FileExistsError("Destination already exists; pass --force to replace it.")
        os.replace(temporary, destination)
        os.chmod(destination, 0o600)
    finally:
        try:
            temporary.unlink()
        except FileNotFoundError:
            pass


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True, help="TI-SERVER config/runtime.example.json")
    parser.add_argument(
        "--destination",
        type=Path,
        default=ROOT / "config" / "private-runtime.json",
        help="Private runtime file path (default: backend config/private-runtime.json)",
    )
    parser.add_argument("--force", action="store_true", help="Replace an existing destination.")
    args = parser.parse_args()
    try:
        install(args.source, args.destination, force=args.force)
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    print("Private runtime config installed and validated; file permissions set to 0600.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
