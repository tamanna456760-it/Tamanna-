# ==========================================
# problem_sync_detect.py
# Problem Sync + Detecting + Input/Output Path
# ==========================================

import os
import json
import shutil
from datetime import datetime

# ==========================================
# CONFIG
# ==========================================

INPUT_PATH = "input/"
OUTPUT_PATH = "output/"
BACKUP_PATH = "backup/"
LOG_FILE = "system_log.txt"

SUPPORTED_FILES = [".py", ".json", ".txt"]

# ==========================================
# CREATE DIRECTORIES
# ==========================================

os.makedirs(INPUT_PATH, exist_ok=True)
os.makedirs(OUTPUT_PATH, exist_ok=True)
os.makedirs(BACKUP_PATH, exist_ok=True)

# ==========================================
# LOGGER
# ==========================================

def write_log(message):

    with open(LOG_FILE, "a", encoding="utf-8") as log:

        log.write(f"{datetime.now()} : {message}\n")

# ==========================================
# FILE DETECTION
# ==========================================

def detect_files():

    print("=" * 60)
    print("FILE DETECTION SYSTEM")
    print("=" * 60)

    files_found = []

    for file in os.listdir(INPUT_PATH):

        full_path = os.path.join(INPUT_PATH, file)

        if os.path.isfile(full_path):

            ext = os.path.splitext(file)[1]

            if ext in SUPPORTED_FILES:

                print(f"[FOUND] {file}")

                files_found.append(full_path)

                write_log(f"Detected file: {file}")

    return files_found

# ==========================================
# PROBLEM DETECTION
# ==========================================

def detect_problems(file_path):

    print(f"\n[SCANNING] {file_path}")

    problems = []

    try:

        with open(file_path, "r", encoding="utf-8") as f:

            content = f.read()

            if "password" in content.lower():

                problems.append("Possible hardcoded password")

            if "token" in content.lower():

                problems.append("Token detected")

            if "eval(" in content:

                problems.append("Unsafe eval() detected")

            if "os.system" in content:

                problems.append("Shell execution found")

    except Exception as e:

        problems.append(str(e))

    return problems

# ==========================================
# FILE BACKUP
# ==========================================

def backup_file(file_path):

    filename = os.path.basename(file_path)

    backup_target = os.path.join(BACKUP_PATH, filename)

    shutil.copy(file_path, backup_target)

    print(f"[BACKUP] {filename}")

    write_log(f"Backup created: {filename}")

# ==========================================
# OUTPUT REPORT
# ==========================================

def generate_report(scan_results):

    report_file = os.path.join(OUTPUT_PATH, "scan_report.json")

    with open(report_file, "w", encoding="utf-8") as report:

        json.dump(scan_results, report, indent=4)

    print(f"\n[REPORT SAVED] {report_file}")

    write_log("Report generated")

# ==========================================
# MAIN SYSTEM
# ==========================================

def main():

    print("=" * 60)
    print("PROBLEM SYNC + DETECT SYSTEM")
    print("=" * 60)

    files = detect_files()

    all_results = {}

    for file in files:

        backup_file(file)

        problems = detect_problems(file)

        all_results[file] = problems

        print(f"\n[RESULT] {file}")

        if problems:

            for p in problems:

                print(f" - {p}")

                write_log(f"{file} : {p}")

        else:

            print(" No problems detected")

    generate_report(all_results)

# ==========================================
# START
# ==========================================

if __name__ == "__main__":

    main()