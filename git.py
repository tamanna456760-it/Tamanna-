#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import importlib.util
from datetime import datetime

ROOT = "."  # current repo root

def now():
    return datetime.utcnow().isoformat() + "Z"

def log(event, detail):
    print(f"[{now()}] 🧠 {event} → {detail}")

def find_tamanna_modules(root):
    py_files = []
    for dirpath, _, filenames in os.walk(root):
        for name in filenames:
            if not name.endswith(".py"):
                continue
            if name in ("tamanna_head_run.py",):
                continue
            full = os.path.join(dirpath, name)
            py_files.append(full)
    return py_files

def load_and_run(path):
    rel = os.path.relpath(path, ROOT)
    log("LOAD", rel)

    spec = importlib.util.spec_from_file_location("tamanna_mod", path)
    mod = importlib.util.module_from_spec(spec)

    try:
        spec.loader.exec_module(mod)
        if hasattr(mod, "main") and callable(mod.main):
            log("RUN", f"{rel} → main()")
            mod.main()
        else:
            log("SKIP", f"{rel} has no main(), only loaded")
    except Exception as e:
        log("ERROR", f"{rel}: {e}")

def main():
    log("HEAD_START", "Tamanna Head Runner শুরু হচ্ছে")
    files = find_tamanna_modules(ROOT)
    log("DISCOVER", f"মোট {len(files)}টা .py ফাইল পাওয়া গেছে")

    for f in files:
        load_and_run(f)

    log("HEAD_END", "সব মডিউল স্ক্যান + রান চেষ্টা শেষ")

if __name__ == "__main__":
    main()
