"""
tamanna_system.py
One-file Tamanna code system:
- Local SQLite DB
- Event add
- Sync to tamanna.io server
- Simple Tamanna commands
- Basic monitor loop
"""

import sqlite3
import time
import requests
from datetime import datetime

# ================== CONFIG ==================

DB_NAME = "tamanna_local.db"
TAMANNA_SERVER_URL = "https://tamanna.io/api/sync"  # নিজের API endpoint বসাও
API_KEY = "YOUR_API_KEY_HERE"  # দরকার হলে auth token

SYNC_INTERVAL_SECONDS = 10  # কত সেকেন্ড পরপর sync করবে

# ================== DB FUNCTIONS ==================

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT NOT NULL,
            synced INTEGER DEFAULT 0,
            created_at TEXT
        )
    """)
    conn.commit()
    conn.close()

def add_event(data: str):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO events (data, synced, created_at) VALUES (?, 0, ?)",
        (data, datetime.utcnow().isoformat())
    )
    conn.commit()
    conn.close()

def get_unsynced_events():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT id, data, created_at FROM events WHERE synced = 0")
    rows = cur.fetchall()
    conn.close()
    return rows

def mark_synced(ids):
    if not ids:
        return
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.executemany("UPDATE events SET synced = 1 WHERE id = ?", [(i,) for i in ids])
    conn.commit()
    conn.close()

def get_stats():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM events")
    total = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM events WHERE synced = 0")
    unsynced = cur.fetchone()[0]
    conn.close()
    return total, unsynced

# ================== SYNC FUNCTION ==================

def sync_events():
    events = get_unsynced_events()
    if not events:
        print("[SYNC] No new events to sync.")
        return

    payload = [
        {"id": row[0], "data": row[1], "created_at": row[2]}
        for row in events
    ]

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }

    try:
        print(f"[SYNC] Sending {len(payload)} events to tamanna.io ...")
        resp = requests.post(TAMANNA_SERVER_URL, json=payload, headers=headers, timeout=10)
        resp.raise_for_status()
        synced_ids = [e["id"] for e in payload]
        mark_synced(synced_ids)
        print(f"[SYNC] OK, synced {len(synced_ids)} events.")
    except Exception as e:
        print("[SYNC] Failed:", e)

# ================== TAMANNA LANGUAGE (SIMPLE) ==================

def run_tamanna_command(cmd: str):
    """
    Simple Tamanna DSL:
    - LOG <text>   -> event add
    - SYNC         -> force sync
    - STATS        -> show DB stats
    """
    cmd = cmd.strip()
    if cmd.upper().startswith("LOG "):
        data = cmd[4:]
        add_event(data)
        print(f"[TAMANNA] Logged event: {data}")
    elif cmd.upper() == "SYNC":
        sync_events()
    elif cmd.upper() == "STATS":
        total, unsynced = get_stats()
        print(f"[TAMANNA] Total events: {total}, Unsynced: {unsynced}")
    else:
        print("[TAMANNA] Unknown command:", cmd)

# ================== MAIN MONITOR LOOP ==================

def main_loop():
    init_db()
    print("=== Tamanna System Started ===")
    print("Commands: LOG <text> | SYNC | STATS | EXIT")
    print("Auto-sync every", SYNC_INTERVAL_SECONDS, "seconds.\n")

    last_sync = 0

    while True:
        # Non-blocking simple input prompt
        try:
            # ছোট delay দিয়ে user input নেবো
            if time.time() - last_sync >= SYNC_INTERVAL_SECONDS:
                sync_events()
                last_sync = time.time()

            # user command নেয়ার চেষ্টা
            print("\nEnter Tamanna command (or press Enter to skip): ", end="", flush=True)
            # input blocking, but simple for demo
            cmd = input()
            if cmd.strip():
                if cmd.strip().upper() == "EXIT":
                    print("Exiting Tamanna system...")
                    break
                run_tamanna_command(cmd)

        except KeyboardInterrupt:
            print("\n[SYS] KeyboardInterrupt, exiting...")
            break

if __name__ == "__main__":
    main_loop()