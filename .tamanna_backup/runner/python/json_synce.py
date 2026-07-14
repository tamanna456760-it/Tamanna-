#!/usr/bin/env python3
"""
JSON File Synchronization
"""

import hashlib
import json
import os
from datetime import datetime


class JSONSync:
    def __init__(self):
        self.sync_file = "sync_state.json"
        self.load_sync_state()

    def load_sync_state(self):
        if os.path.exists(self.sync_file):
            with open(self.sync_file, "r") as f:
                self.sync_state = json.load(f)
        else:
            self.sync_state = {"files": {}}

    def save_sync_state(self):
        with open(self.sync_file, "w") as f:
            json.dump(self.sync_state, f, indent=2)

    def get_file_hash(self, file_path):
        with open(file_path, "rb") as f:
            return hashlib.md5(f.read()).hexdigest()

    def sync_json_files(self):
        print("🔄 Synchronizing JSON files...")

        for root, dirs, files in os.walk("."):
            for file in files:
                if file.endswith(".json"):
                    file_path = os.path.join(root, file)
                    current_hash = self.get_file_hash(file_path)

                    # Check if file changed
                    if (
                        file_path not in self.sync_state["files"]
                        or self.sync_state["files"][file_path]["hash"] != current_hash
                    ):

                        print(f"📄 Syncing: {file_path}")

                        # Update sync state
                        self.sync_state["files"][file_path] = {
                            "hash": current_hash,
                            "last_sync": datetime.now().isoformat(),
                            "size": os.path.getsize(file_path),
                        }

        self.save_sync_state()
        print("✅ JSON file sync completed!")


def main():
    sync = JSONSync()
    sync.sync_json_files()


if __name__ == "__main__":
    main()
