#!/usr/bin/env python3
# IT TAMANNA FULL AI POWER SYSTEM
# User: tamanna456760-it

import json
import os
import platform
import shutil
import subprocess
import sys
from datetime import datetime

# -------------------- CONFIG --------------------
BASE = "tamanna_system"
SRC = f"{BASE}/source"
BAK = f"{BASE}/backup"
BUILD = f"{BASE}/build"
SNAP = f"{BASE}/snapshots"
STATUS = f"{BASE}/system_status.json"
# ------------------------------------------------

# -------------------- SETUP --------------------
def banner():
    print("="*55)
    print(" 🤖⚡ IT TAMANNA FULL AI POWER SYSTEM ")
    print(" User: tamanna456760-it ")
    print("="*55)

def setup():
    for d in [BASE, SRC, BAK, BUILD, SNAP]:
        os.makedirs(d, exist_ok=True)
# ------------------------------------------------

# -------------------- CORE FUNCTIONS --------------------
def sync():
    c = 0
    for r,_,fs in os.walk(SRC):
        for f in fs:
            s = os.path.join(r,f)
            d = s.replace(SRC, BAK)
            os.makedirs(os.path.dirname(d), exist_ok=True)
            shutil.copy2(s,d)
            c += 1
    print(f"🔄 Synced {c} files")

def status():
    data = {
        "time": str(datetime.now()),
        "os": platform.system(),
        "platform": platform.platform()
    }
    with open(STATUS,"w") as f:
        json.dump(data, f, indent=2)
    print("📊 System status saved")

def build():
    with open(f"{BUILD}/build.txt","w") as f:
        f.write("Build OK\n")
        f.write(str(datetime.now()))
    print("🔧 Build completed")

# -------------------- AI FUNCTIONS --------------------
def ai_rate():
    score = 0
    files = 0
    for r,_,fs in os.walk(SRC):
        for f in fs:
            if f.endswith(".py"):
                files += 1
                try:
                    p = os.path.join(r,f)
                    lines = open(p, errors="ignore").readlines()
                    score += min(10, len(lines)//20 + sum(1 for l in lines if "#" in l))
                except:
                    pass
    if files == 0:
        print("🧠 No Python files to rate")
        return
    rating = round(min(10, score / files), 1)
    print(f"🧠 AI Code Rating: {rating}/10")

def ai_summary():
    files = []
    for r,_,fs in os.walk(SRC):
        for f in fs:
            files.append(f)
    print("🧠 AI Summary:")
    print(f"- Total files: {len(files)}")
    print("- Project looks like a multi-file code system")

def ai_suggest():
    print("🧠 AI Suggestions:")
    print("- Add README.md")
    print("- Add version control (Git)")
    print("- Organize files by type")
    print("- Backup regularly")

# -------------------- SNAPSHOT --------------------
def save_snapshot():
    t = datetime.now().strftime("%Y%m%d_%H%M%S")
    dest = f"{SNAP}/snapshot_{t}"
    shutil.copytree(SRC, dest)
    print(f"💾 Snapshot saved: {dest}")

# -------------------- RUN POWER --------------------
def run_file(cmd):
    parts = cmd.split(" ",1)
    if len(parts)<2:
        print("❌ Usage: run filename.py")
        return
    name = parts[1]
    path = os.path.join(SRC, name)
    if not path.endswith(".py"):
        print("❌ Only .py files allowed")
        return
    if not os.path.exists(path):
        print("❌ File not found")
        return
    print(f"⚡ Running {name}")
    subprocess.run(["python3", path])

# -------------------- HELP --------------------
def help_menu():
    print("""
Commands:
 build        → build project
 sync         → sync files
 status       → save system status
 ai rate      → rate code quality
 ai summary   → summary of files
 ai suggest   → AI suggestions
 save         → save snapshot
 run file.py  → run python file
 exit         → quit
""")

# -------------------- MAIN --------------------
def main():
    banner()
    setup()
    help_menu()

    # Check if interactive terminal is available
    interactive = sys.stdin.isatty()

    # Non-interactive / playground commands
    if not interactive:
        print("⚡ Running in non-interactive mode...")
        commands = ["build","sync","ai rate","ai summary","ai suggest","save"]
        for cmd in commands:
            print(f"IT@tamanna-power:~$ {cmd}")
            execute_command(cmd)
        return

    # Interactive mode
    while True:
        try:
            cmd = input("IT@tamanna-power:~$ ").strip()
        except EOFError:
            print("\n👋 Exiting...")
            break
        if cmd.lower() in ["exit","quit"]:
            print("👋 Exiting...")
            break
        execute_command(cmd)

def execute_command(cmd):
    if cmd == "build":
        build()
    elif cmd == "sync":
        sync()
    elif cmd == "status":
        status()
    elif cmd == "ai rate":
        ai_rate()
    elif cmd == "ai summary":
        ai_summary()
    elif cmd == "ai suggest":
        ai_suggest()
    elif cmd == "save":
        save_snapshot()
    elif cmd.startswith("run "):
        run_file(cmd)
    else:
        print("❌ Unknown command (type help)")

if __name__ == "__main__":
    main()