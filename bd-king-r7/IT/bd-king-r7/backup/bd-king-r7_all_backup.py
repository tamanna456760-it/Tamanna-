# r7_total_backup.py
# Sovereign multi-root backup for bd_king_r7: code + panels + AI + control plane
import os, sys, shutil, hashlib, json, datetime, stat

# -------- CONFIGURE THESE --------
CONFIG = {
    "modules": [
        # Fill with actual paths
        {"name": "core_r7",         "path": "/path/to/bd_king_r7"},
        {"name": "tamanna_ai",      "path": "/path/to/tamanna"},
        {"name": "ai_panels",       "path": "/path/to/ai_panels"},
        {"name": "master_control",  "path": "/path/to/master_control_panel"},
        {"name": "utilities",       "path": "/path/to/utilities"}
    ],
    "exclude_dirs": {".git", ".cache", "__pycache__", ".venv", "node_modules", "build", "dist"},
    "exclude_patterns": {".DS_Store"},
    "backup_root": "/path/to/R7_BACKUP_ROOT",
    "make_zip_snapshot": True  # creates a zip of the full mirror for easy transport
}
# ---------------------------------

def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def stamp():
    return datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

def include_rel(relpath, exclude_dirs, exclude_patterns):
    parts = relpath.split(os.sep)
    if any(p in exclude_dirs for p in parts if p):
        return False
    base = os.path.basename(relpath)
    if base in exclude_patterns:
        return False
    return True

def copy_with_dirs(src, dst):
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copy2(src, dst)

def record_permissions(path):
    try:
        st = os.stat(path)
        return {
            "mode": stat.S_IMODE(st.st_mode),
            "uid": getattr(st, "st_uid", None),
            "gid": getattr(st, "st_gid", None)
        }
    except Exception:
        return {"mode": None, "uid": None, "gid": None}

def backup_module(session_dir, module):
    name = module["name"]
    src_root = os.path.abspath(module["path"])
    files_dir = os.path.join(session_dir, "files", name)
    mirror_dir = os.path.join(session_dir, "mirror", name)
    os.makedirs(files_dir, exist_ok=True)
    os.makedirs(mirror_dir, exist_ok=True)

    entries = []
    counts = {"files": 0, "bytes": 0}

    for root, dirs, files in os.walk(src_root):
        rel_root = os.path.relpath(root, src_root)
        if rel_root == ".":
            rel_root = ""
        dirs[:] = [d for d in dirs if include_rel(os.path.join(rel_root, d),
                                                  CONFIG["exclude_dirs"], CONFIG["exclude_patterns"])]
        for fname in files:
            relpath = os.path.join(rel_root, fname)
            if not include_rel(relpath, CONFIG["exclude_dirs"], CONFIG["exclude_patterns"]):
                continue
            src = os.path.join(src_root, relpath)
            dst_file = os.path.join(files_dir, relpath)
            dst_mirror = os.path.join(mirror_dir, relpath)

            os.makedirs(os.path.dirname(dst_file), exist_ok=True)
            os.makedirs(os.path.dirname(dst_mirror), exist_ok=True)

            shutil.copy2(src, dst_file)
            shutil.copy2(src, dst_mirror)

            h = sha256(src)
            size = os.path.getsize(src)
            perm = record_permissions(src)
            entry = {
                "module": name,
                "path": relpath.replace("\\", "/"),
                "size": size,
                "sha256": h,
                "permissions": perm
            }
            entries.append(entry)
            counts["files"] += 1
            counts["bytes"] += size
            print(f"[AFFIRM] {name}/{relpath} [{size} bytes] -> {h}")

    return {"name": name, "source_root": src_root, "counts": counts, "entries": entries}

def write_manifest(session_dir, module_reports):
    manifest = {
        "system": "bd_king_r7_total",
        "session": os.path.basename(session_dir),
        "created_at": datetime.datetime.now().isoformat(),
        "modules": [],
        "totals": {"files": 0, "bytes": 0}
    }
    for rep in module_reports:
        manifest["modules"].append({
            "name": rep["name"],
            "source_root": rep["source_root"],
            "counts": rep["counts"]
        })
        manifest["totals"]["files"] += rep["counts"]["files"]
        manifest["totals"]["bytes"] += rep["counts"]["bytes"]

    # entries index saved separately for compactness
    entries_path = os.path.join(session_dir, "entries.jsonl")
    with open(entries_path, "w", encoding="utf-8") as f:
        for rep in module_reports:
            for e in rep["entries"]:
                f.write(json.dumps(e, ensure_ascii=False) + "\n")

    manifest_path = os.path.join(session_dir, "manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    root_hash = hashlib.sha256(json.dumps(manifest, sort_keys=True).encode()).hexdigest()
    seals_path = os.path.join(session_dir, "seals.txt")
    with open(seals_path, "w", encoding="utf-8") as f:
        f.write(f"R7_TOTAL_BACKUP {manifest['session']}\n")
        f.write(f"MODULES {len(manifest['modules'])}\n")
        f.write(f"FILES {manifest['totals']['files']}\n")
        f.write(f"BYTES {manifest['totals']['bytes']}\n")
        f.write(f"MANIFEST_SHA256 {root_hash}\n")
        f.write("EVERY FILE WITNESSED. EVERY HASH SEALED.\n")

    return manifest_path, seals_path, entries_path

def zip_snapshot(session_dir):
    base_dir = os.path.join(session_dir, "mirror")
    zip_base = os.path.join(session_dir, "snapshot_zip", "r7_mirror")
    os.makedirs(os.path.dirname(zip_base), exist_ok=True)
    archive = shutil.make_archive(zip_base, 'zip', base_dir)
    print(f"[SNAPSHOT] Zip created: {archive}")
    return archive

def main():
    session_name = f"R7_TOTAL_{stamp()}"
    backup_root = os.path.abspath(CONFIG["backup_root"])
    session_dir = os.path.join(backup_root, session_name)
    os.makedirs(session_dir, exist_ok=True)
    os.makedirs(os.path.join(session_dir, "files"), exist_ok=True)
    os.makedirs(os.path.join(session_dir, "mirror"), exist_ok=True)

    reports = []
    for module in CONFIG["modules"]:
        if not os.path.isdir(module["path"]):
            print(f"[WARN] Missing module path: {module['name']} -> {module['path']}")
            continue
        reports.append(backup_module(session_dir, module))

    manifest_path, seals_path, entries_path = write_manifest(session_dir, reports)
    print(f"\n[COMPLETE] Backup sealed.\nSession:   {session_dir}\nManifest:  {manifest_path}\nSeals:     {seals_path}\nEntries:   {entries_path}")

    if CONFIG["make_zip_snapshot"]:
        zip_snapshot(session_dir)

if __name__ == "__main__":
    # Optional CLI override: python r7_total_backup.py /custom/backup/root
    if len(sys.argv) >= 2:
        CONFIG["backup_root"] = sys.argv[1]
    main()
