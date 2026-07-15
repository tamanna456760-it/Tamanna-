# ==========================================
# auto_fix_generator.py
# Auto Fix + Generate File System
# ==========================================

import json
import os
from datetime import datetime

# ==========================================
# PATH CONFIG
# ==========================================

INPUT_PATH = "input/"
FIXED_PATH = "fixed/"
LOG_FILE = "auto_fix_log.txt"

os.makedirs(INPUT_PATH, exist_ok=True)
os.makedirs(FIXED_PATH, exist_ok=True)

# ==========================================
# LOGGER
# ==========================================

def write_log(message):

    with open(LOG_FILE, "a", encoding="utf-8") as log:

        log.write(f"{datetime.now()} : {message}\n")

# ==========================================
# FIX ENGINE
# ==========================================

def fix_code(content):

    fixes = []

    # --------------------------------------
    # Remove dangerous eval()
    # --------------------------------------

    if "eval(" in content:

        content = content.replace("eval(", "# BLOCKED_eval(")

        fixes.append("Blocked eval()")

    # --------------------------------------
    # Remove shell execution
    # --------------------------------------

    if "os.system(" in content:

        content = content.replace("os.system(", "# BLOCKED_os.system(")

        fixes.append("Blocked os.system()")

    # --------------------------------------
    # Hide tokens
    # --------------------------------------

    if "token" in content.lower():

        content = content.replace("token", "SAFE_TOKEN")

        fixes.append("Protected token")

    # --------------------------------------
    # Hide passwords
    # --------------------------------------

    if "password" in content.lower():

        content = content.replace("password", "SAFE_PASSWORD")

        fixes.append("Protected password")

    return content, fixes

# ==========================================
# PROCESS FILE
# ==========================================

def process_file(file_path):

    filename = os.path.basename(file_path)

    print(f"\n[PROCESSING] {filename}")

    try:

        with open(file_path, "r", encoding="utf-8") as f:

            content = f.read()

        fixed_content, fixes = fix_code(content)

        fixed_file = os.path.join(FIXED_PATH, f"fixed_{filename}")

        with open(fixed_file, "w", encoding="utf-8") as out:

            out.write(fixed_content)

        print(f"[FIXED] {fixed_file}")

        write_log(f"{filename} fixed successfully")

        if fixes:

            print("[APPLIED FIXES]")

            for fx in fixes:

                print(f" - {fx}")

                write_log(f"{filename} : {fx}")

        else:

            print("No fixes needed")

    except Exception as e:

        print(f"[ERROR] {e}")

        write_log(str(e))

# ==========================================
# MAIN SYSTEM
# ==========================================

def main():

    print("=" * 60)
    print("AUTO FIX GENERATOR SYSTEM")
    print("=" * 60)

    files = os.listdir(INPUT_PATH)

    for file in files:

        full_path = os.path.join(INPUT_PATH, file)

        if os.path.isfile(full_path):

            process_file(full_path)

    print("\nAll files processed")

# ==========================================
# START
# ==========================================

if __name__ == "__main__":

    main()