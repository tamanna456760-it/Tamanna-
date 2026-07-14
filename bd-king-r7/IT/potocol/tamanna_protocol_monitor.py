import json
import os
import time
from datetime import datetime

LOG_FILE = "protocol_monitor.log"

WATCH_EXTENSIONS = [".py", ".js", ".json", ".html", ".css", ".sh"]

file_state = {}


def write_log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {message}"

    print(line)

    with open(LOG_FILE, "a", encoding="utf-8") as log:
        log.write(line + "\n")


def scan_files():
    global file_state

    for root, dirs, files in os.walk("."):
        if ".git" in root:
            continue

        for file in files:
            path = os.path.join(root, file)

            if not any(file.endswith(ext) for ext in WATCH_EXTENSIONS):
                continue

            try:
                modified = os.path.getmtime(path)

                if path not in file_state:
                    file_state[path] = modified
                    write_log(f"NEW FILE: {path}")

                elif file_state[path] != modified:
                    file_state[path] = modified
                    write_log(f"MODIFIED: {path}")

            except Exception as e:
                write_log(f"ERROR: {path} -> {e}")


def main():
    write_log("Tamanna Protocol Monitor Started")

    while True:
        scan_files()
        time.sleep(5)


if __name__ == "__main__":
    main()
