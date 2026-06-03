# r7_backup.py
# Sovereign full-system backup for bd_king_r7 — snapshot + file-by-file + manifest + seals
import datetime
import hashlib
import json
import os
import shutil
import sys


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def stamp():
    return datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


def should_include(relpath):
    # Customize filters here
    EXCLUDE_DIRS = {
        ".git",
        ".cache",
        "__pycache__",
        ".venv",
        "node_modules",
        "build",
        "dist",
    }
    parts = relpath.split(os.sep)
    if any(p in EXCLUDE_DIRS for p in parts):
        return False
    return True


def copy_file(src, dst):
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copy2(src, dst)


def main():
    if len(sys.argv) < 3:
        print("Usage: python r7_backup.py <SOURCE_ROOT> <BACKUP_ROOT>")
        sys.exit(1)

    src_root = os.path.abspath(sys.argv[1])
    backup_root = os.path.abspath(sys.argv[2])
    session = stamp()
    session_dir = os.path.join(backup_root, f"R7_BACKUP_{session}")
    files_dir = os.path.join(session_dir, "files")
    snapshot_dir = os.path.join(session_dir, "snapshot")
    manifest_path = os.path.join(session_dir, "manifest.json")
    seals_path = os.path.join(session_dir, "seals.txt")

    os.makedirs(files_dir, exist_ok=True)
    os.makedirs(snapshot_dir, exist_ok=True)

    manifest = {
        "system": "bd_king_r7",
        "source_root": src_root,
        "backup_root": backup_root,
        "session": session,
        "counts": {"files": 0, "bytes": 0},
        "entries": [],
    }

    # Snapshot: tar-like copy (directory mirror)
    print("Mirroring snapshot directory...")
    for root, dirs, files in os.walk(src_root):
        rel_root = os.path.relpath(root, src_root)
        if rel_root == ".":
            rel_root = ""
        # Apply exclude filter to dirs
        dirs[:] = [d for d in dirs if should_include(
            os.path.join(rel_root, d))]
        for name in files:
            relpath = os.path.join(rel_root, name)
            if not should_include(relpath):
                continue
            src = os.path.join(src_root, relpath)
            dst_snapshot = os.path.join(snapshot_dir, relpath)
            dst_files = os.path.join(files_dir, relpath)

            # Copy to snapshot mirror
            os.makedirs(os.path.dirname(dst_snapshot), exist_ok=True)
            shutil.copy2(src, dst_snapshot)

            # Copy file-by-file
            os.makedirs(os.path.dirname(dst_files), exist_ok=True)
            shutil.copy2(src, dst_files)

            # Hash and record
            h = sha256(src)
            size = os.path.getsize(src)
            manifest["counts"]["files"] += 1
            manifest["counts"]["bytes"] += size
            manifest["entries"].append(
                {"path": relpath.replace("\\", "/"), "size": size, "sha256": h}
            )

            print(f"[AFFIRM] {relpath} [{size} bytes] -> SHA256 {h}")

    # Write manifest
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    # Seals: a human-readable integrity chant
    total_bytes = manifest["counts"]["bytes"]
    total_files = manifest["counts"]["files"]
    root_hash = hashlib.sha256(
        json.dumps(manifest, sort_keys=True).encode()
    ).hexdigest()
    with open(seals_path, "w", encoding="utf-8") as f:
        f.write(f"BD_KING_R7_BACKUP_SESSION {session}\n")
        f.write(f"FILES {total_files}\n")
        f.write(f"BYTES {total_bytes}\n")
        f.write(f"MANIFEST_SHA256 {root_hash}\n")
        f.write("EVERY FILE WITNESSED. EVERY HASH SEALED.\n")

    print("\n[COMPLETE] Backup sealed.")
    print(f"Session dir: {session_dir}")
    print(f"Manifest:    {manifest_path}")
    print(f"Seals:       {seals_path}")
    print(f"Root seal:   {root_hash}")


if __name__ == "__main__":
    main()
