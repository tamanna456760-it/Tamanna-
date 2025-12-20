#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import hashlib
import json
from datetime import datetime

TAMANNAPATH = "Tamanna"         # তোমার Tamanna ফোল্ডার
HEAD_INDEX  = "tamanna_head_index.jsonl"  # head sync log

class TamannaHead:
    def __init__(self, root=TAMANNAPATH):
        self.root = root
        self.files = {}   # key = rel_path, value = info dict
        self.last_snapshot = {}

    # ---------- Utility ----------
    def now(self):
        return datetime.utcnow().isoformat() + "Z"

    def sha256(self, path):
        h = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                h.update(chunk)
        return h.hexdigest()

    def log_head(self, kind, detail):
        entry = {
            "time": self.now(),
            "kind": kind,
            "detail": detail
        }
        print("🧠 HEAD:", entry)
        with open(HEAD_INDEX, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    # ---------- Scan all files ----------
    def scan_files(self):
        files = {}
        if not os.path.isdir(self.root):
            self.log_head("error", f"Root path not found: {self.root}")
            return files

        for dirpath, _, filenames in os.walk(self.root):
            for name in filenames:
                full = os.path.join(dirpath, name)
                rel = os.path.relpath(full, self.root)
                try:
                    size = os.path.getsize(full)
                    digest = self.sha256(full)
                except Exception as e:
                    self.log_head("scan_error", {"file": rel, "error": str(e)})
                    continue

                files[rel] = {
                    "path": rel,
                    "size": size,
                    "hash": digest,
                }
        return files

    # ---------- Build + sync head ----------
    def sync_head(self):
        self.log_head("sync_start", f"Scanning {self.root}")
        current = self.scan_files()

        # First time or no previous snapshot
        if not self.last_snapshot:
            self.last_snapshot = current
            self.files = current
            self.log_head("sync_init", {
                "file_count": len(current),
                "message": "Tamanna head initialized with all files."
            })
            return

        # Compare previous vs current
        prev = self.last_snapshot
        added   = set(current) - set(prev)
        removed = set(prev)    - set(current)
        changed = {p for p in current if p in prev and current[p]["hash"] != prev[p]["hash"]}

        self.files = current
        self.last_snapshot = current

        self.log_head("sync_result", {
            "total": len(current),
            "added": sorted(list(added)),
            "removed": sorted(list(removed)),
            "changed": sorted(list(changed)),
        })

    # ---------- Heartbeat ----------
    def heartbeat(self):
        info = {
            "files_total": len(self.files),
            "time": self.now()
        }
        self.log_head("heartbeat", info)

    # ---------- Integrity check ----------
    def integrity_check(self):
        # তুলনা করার জন্য আবার scan
        current = self.scan_files()
        prev = self.files

        added   = set(current) - set(prev)
        removed = set(prev)    - set(current)
        changed = {p for p in current if p in prev and current[p]["hash"] != prev[p]["hash"]}

        if not added and not removed and not changed:
            self.log_head("integrity_ok", "All files match head state.")
        else:
            self.log_head("integrity_alert", {
                "added": sorted(list(added)),
                "removed": sorted(list(removed)),
                "changed": sorted(list(changed)),
            })
        # head update করতে চাইলে:
        self.files = current

# ---- ডেমো রান ----
if __name__ == "__main__":
    head = TamannaHead()
    head.sync_head()        # প্রথমবার সব sync
    head.heartbeat()        # এখনকার head অবস্থা
    head.integrity_check()  # আবার দেখে সব ঠিক আছে কিনা
