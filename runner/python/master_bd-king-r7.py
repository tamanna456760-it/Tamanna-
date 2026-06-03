#!/usr/bin/env python3
# BD-KING-R7 POWERHUB MASTER SYSTEM
# User: tamanna456760-it

import os, shutil, json, platform, subprocess
from datetime import datetime
import psutil  # system resource monitoring

# -------------------- CONFIG --------------------
BASE = "bd_king_r7_powerhub"
SRC = f"{BASE}/source"
BACKUP = f"{BASE}/backup"
BUILD = f"{BASE}/build"
SNAP = f"{BASE}/snapshots"
STATUS = f"{BASE}/system_status.json"
VERSION_HASH = "4711158de8b99a6da04d0df615779244d0cae12d"

# -------------------- SETUP --------------------
def banner():
    print("="*60)
    print(" ⚡ BD-KING-R7 POWERHUB MASTER SYSTEM ")
    print(" User: tamanna456760-it ")
    print(f" Version: {VERSION_HASH}")
    print("="*60)

def setup_dirs():
    for d in [BASE, SRC, BACKUP, BUILD, SNAP]:
        os.makedirs(d, exist_ok=True)

# -------------------- CORE FUNCTIONS --------------------
def sync_files():
    count = 0
    for r,_,files in os.walk(SRC):
        for f in files:
            s = os.path.join(r,f)
            d = s.replace(SRC, BACKUP)
            os.makedirs(os.path.dirname(d), exist_ok=True)
            shutil.copy2(s,d)
            count += 1
    print(f"🔄 Synced {count} files")

def build_project():
    with open(f"{BUILD}/build_info.txt","w") as f:
        f.write("BD-KING-R7 Build Complete\n")
        f.write(str(datetime.now()))
    print("🔧 Build completed")

def save_snapshot():
    t = datetime.now().strftime("%Y%m%d_%H%M%S")
    dest = f"{SNAP}/snapshot_{t}"
    shutil.copytree(SRC, dest)
    with open(os.path.join(dest,"version.txt"),"w") as f:
        f.write(f"Version: {VERSION_HASH}\nSaved at: {t}")
    print(f"💾 Snapshot saved: {dest}")

def system_status():
    status = {
        "time": str(datetime.now()),
        "os": platform.system(),
        "platform": platform.platform(),
        "cpu_percent": psutil.cpu_percent(interval=1),
        "memory_percent": psutil.virtual_memory().percent,
        "disk_percent": psutil.disk_usage("/").percent
    }
    with open(STATUS,"w") as f:
        json.dump(status, f, indent=4)
    print(f"📊 System status saved | CPU: {status['cpu_percent']}%, RAM: {status['memory_percent']}%, Disk: {status['disk_percent']}%")

# -------------------- AI CODE FUNCTIONS --------------------
def ai_rate():
    score = 0
    files = 0
    for r,_,fs in os.walk(SRC):
        for f in fs:
            if f.endswith(".py"):
                files += 1
                try:
                    path = os.path.join(r,f)
                    lines = open(path,errors="ignore").readlines()
                    score += min(10,len(lines)//20 + sum(1 for l in lines if "#" in l))
                except:
                    pass
    if files==0:
        print("🧠 No Python files to rate")
        return
    rating = round(min(10, score/files),1)
    print(f"🧠 AI Code Rating: {rating}/10")

def ai_summary():
    files = []
    for r,_,fs in os.walk(SRC):
        for f in fs:
            files.append(f)
    print(f"🧠 AI Summary: Total files: {len(files)}")

def ai_suggest():
    print("🧠 AI Suggestions:\n- Add README.md\n- Use Git\n- Organize files\n- Backup regularly")

# -------------------- RUN PYTHON FILES --------------------
def run_file(cmd):
    parts = cmd.split(" ",1)
    if len(parts)<2:
        print("❌ Usage: run filename.py")
        return
    name = parts[1]
    path = os.path.join(SRC,name)
    if not path.endswith(".py"):
        print("❌ Only .py files allowed")
        return
    if not os.path.exists(path):
        print("❌ File not found")
        return
    print(f"⚡ Running {name}")
    subprocess.run(["python3", path])

# -------------------- HELP MENU --------------------
def help_menu():
    print("""
Commands:
 build        → build project
 sync         → sync files
 status       → system resource status
 ai rate      → rate Python code
 ai summary   → file summary
 ai suggest   → AI suggestions
 save         → save snapshot
 run file.py  → run Python file
 exit         → quit
""")

# -------------------- MAIN --------------------
def main():
    banner()
    setup_dirs()
    help_menu()

    import sys
    interactive = sys.stdin.isatty()
    if not interactive:
        # Non-interactive demo commands
        cmds = ["build","sync","ai rate","ai summary","ai suggest","status","save"]
        for c in cmds:
            print(f"BD-KING-R7: Running {c}")
            execute_command(c)
        return

    # Interactive terminal
    while True:
        try:
            cmd = input("BD-KING-R7> ").strip()
        except EOFError:
            print("\n👋 Exiting...")
            break
        if cmd.lower() in ["exit","quit"]:
            print("👋 Exiting...")
            break
        execute_command(cmd)

def execute_command(cmd):
    if cmd=="build":
        build_project()
    elif cmd=="sync":
        sync_files()
    elif cmd=="status":
        system_status()
    elif cmd=="ai rate":
        ai_rate()
    elif cmd=="ai summary":
        ai_summary()
    elif cmd=="ai suggest":
        ai_suggest()
    elif cmd=="save":
        save_snapshot()
    elif cmd.startswith("run "):
        run_file(cmd)
    else:
        print("❌ Unknown command (type help)")

if __name__=="__main__":
    main()