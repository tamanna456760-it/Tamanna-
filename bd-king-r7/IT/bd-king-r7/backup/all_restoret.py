# r7_total_restore.py
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


def load_entries(entries_path):
    entries = []
    with open(entries_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                entries.append(json.loads(line))
    return entries


def main():
    if len(sys.argv) < 3:
        print(
            "Usage: python r7_total_restore.py <SESSION_DIR> <TARGET_DIR> [MODULE_NAME]"
        )
        sys.exit(1)

    session_dir = os.path.abspath(sys.argv[1])
    target_dir = os.path.abspath(sys.argv[2])
    module_name = sys.argv[3] if len(sys.argv) >= 4 else None

    entries_path = os.path.join(session_dir, "entries.jsonl")
    files_root = os.path.join(session_dir, "files")
    entries = load_entries(entries_path)

    mismatches, restored = [], 0
    for e in entries:
        if module_name and e["module"] != module_name:
            continue
        src = os.path.join(files_root, e["module"], e["path"])
        dst = os.path.join(target_dir, e["module"], e["path"])
        if not os.path.exists(src):
            mismatches.append((e["module"], e["path"], "missing"))
            continue
        h = sha256(src)
        if h != e["sha256"]:
            mismatches.append((e["module"], e["path"], "hash mismatch"))
            continue
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(src, dst)
        restored += 1
        print(f"[REVIVAL] {e['module']}/{e['path']}")

    print(f"\nRestored files: {restored}")
    if mismatches:
        print("Issues:")
        for m in mismatches:
            print(f" - {m[0]}/{m[1]}: {m[2]}")
    else:
        print("All files restored with integrity.")


if __name__ == "__main__":
    main()
