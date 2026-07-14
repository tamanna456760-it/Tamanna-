import os
import shutil
import subprocess
import time

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

CONFIG_PATH = "config.json"

import json


def load_config():
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)


config = load_config()

WATCH_FOLDER = config["watch_folder"]
RULES = config["rules"]


def run_file(file_path):
    try:
        ext = file_path.split(".")[-1]
        if ext == "py":
            subprocess.Popen(["python", file_path])
        elif ext == "js":
            subprocess.Popen(["node", file_path])
    except Exception as e:
        print("Run error:", e)


def move_file(file_path, dest_folder):
    os.makedirs(dest_folder, exist_ok=True)
    shutil.move(file_path, os.path.join(dest_folder, os.path.basename(file_path)))


class Handler(FileSystemEventHandler):

    def on_modified(self, event):
        if event.is_directory:
            return
        self.process(event.src_path)

    def on_created(self, event):
        if event.is_directory:
            return
        self.process(event.src_path)

    def process(self, path):
        ext = path.split(".")[-1]

        # auto move rules
        for rule in RULES:
            if ext in rule["ext"]:
                move_file(path, rule["folder"])
                print(f"Moved {path} -> {rule['folder']}")
                return

        # auto run rules
        if config["auto_run"]:
            run_file(path)
            print(f"Executed: {path}")


if __name__ == "__main__":
    event_handler = Handler()
    observer = Observer()
    observer.schedule(event_handler, WATCH_FOLDER, recursive=True)

    print("🚀 Monitoring started...")
    observer.start()

    try:
        while True:
            time.sleep(2)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()
