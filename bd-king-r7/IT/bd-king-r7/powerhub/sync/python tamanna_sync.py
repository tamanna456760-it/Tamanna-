#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
TAMANNA SYNC ENGINE
-------------------
Auto-sync all files and code from SOURCE to TARGET.

- Scans every file and folder inside SOURCE
- Copies new files to TARGET
- Updates files if changed (by size or modified time)
- Creates missing folders in TARGET
- Logs every action in tamanna_sync.log

Edit the CONFIG section only.
"""

import os
import shutil
import time
import hashlib
from datetime import datetime

# ====================== CONFIG: EDIT THESE ONLY ======================

# **Source folder:** where your original files & code live
SOURCE_DIR = r"/path/to/source"

# **Target folder:** where you want everything synced (backup / mirror)
TARGET_DIR = r"/path/to/target"

# **Log file name** (will be created in the same folder as this script)
LOG_FILE = "tamanna_sync.log"

# **If True:** compare file size + modified time only (faster)
# **If False:** compare SHA256 hash (slower, but more exact)
FAST_COMPARE = True

# ====================== END CONFIG ======================


def log(message: str) -> None:
    """Write a timestamped line into the log file and print it."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {message}"
    print(line)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def file_hash(path: str, chunk_size: int = 1024 * 1024) -> str:
    """Calculate SHA256 hash of a file."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def files_different(src: str, dst: str) -> bool:
    """Return True if files are different (by size+mtime or hash)."""
    if not os.path.exists(dst):
        return True

    src_stat = os.stat(src)
    dst_stat = os.stat(dst)

    if FAST_COMPARE:
        # Compare size and modified time
        if src_stat.st_size != dst_stat.st_size:
            return True
        # Allow tiny mtime difference
        if abs(src_stat.st_mtime - dst_stat.st_mtime) > 0.5:
            return True
        return False
    else:
        # Full hash compare
        return file_hash(src) != file_hash(dst)


def ensure_directory(path: str) -> None:
    """Create directory if it does not exist."""
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)
        log(f"CREATE DIR  : {path}")


def sync_file(src: str, dst: str) -> None:
    """Copy one file from src to dst if needed."""
    if files_different(src, dst):
        ensure_directory(os.path.dirname(dst))
        shutil.copy2(src, dst)
        log(f"COPY/UPDATE : {src} -> {dst}")
    else:
        # Optional: uncomment if you want to log unchanged files
        # log(f"SKIP SAME   : {src}")
        pass


def tamanna_sync(source: str, target: str) -> None:
    """Main sync function: walk through source and mirror into target."""
    if not os.path.exists(source):
        log(f"ERROR: SOURCE DIR NOT FOUND: {source}")
        return

    ensure_directory(target)
    log("--------------------------------------------------")
    log("TAMANNA SYNC START")
    log(f"SOURCE : {source}")
    log(f"TARGET : {target}")
    log(f"FAST_COMPARE : {FAST_COMPARE}")
    log("--------------------------------------------------")

    total_files = 0
    start_time = time.time()

    for root, dirs, files in os.walk(source):
        # Build relative path from source root
        rel_path = os.path.relpath(root, source)
        if rel_path == ".":
            rel_path = ""

        # Mirror directory structure
        target_root = os.path.join(target, rel_path)
        ensure_directory(target_root)

        # Sync files
        for name in files:
            src_path = os.path.join(root, name)
            dst_path = os.path.join(target_root, name)
            sync_file(src_path, dst_path)
            total_files += 1

    elapsed = time.time() - start_time
    log(f"TAMANNA SYNC DONE | FILES: {total_files} | TIME: {elapsed:.2f}s")
    log("--------------------------------------------------")


if __name__ == "__main__":
    tamanna_sync(SOURCE_DIR, TARGET_DIR)
