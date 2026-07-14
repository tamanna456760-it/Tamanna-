#!/usr/bin/env python3

import json
from datetime import datetime
from pathlib import Path

class TamannaBrain:

    def __init__(self):
        self.name = "Tamanna AI"
        self.version = "1.0.0"
        self.started = datetime.now().isoformat()

        self.memory = {
            "status": "online",
            "tasks_completed": 0,
            "last_command": None
        }

    def info(self):
        return {
            "name": self.name,
            "version": self.version,
            "started": self.started,
            "memory": self.memory
        }

    def execute(self, command):
        self.memory["last_command"] = command
        self.memory["tasks_completed"] += 1

        commands = {
            "status": self.status,
            "health": self.health,
            "save": self.save_memory,
            "help": self.help
        }

        func = commands.get(command)

        if func:
            return func()

        return {
            "success": False,
            "message": f"Unknown command: {command}"
        }

    def status(self):
        return {
            "success": True,
            "status": self.memory["status"]
        }

    def health(self):
        return {
            "success": True,
            "cpu": "unknown",
            "memory": "unknown",
            "disk": "unknown"
        }

    def save_memory(self):
        Path("data").mkdir(exist_ok=True)

        with open("data/brain_memory.json", "w") as f:
            json.dump(self.memory, f, indent=4)

        return {
            "success": True,
            "message": "Memory saved."
        }

    def help(self):
        return {
            "commands": [
                "status",
                "health",
                "save",
                "help"
            ]
        }


if __name__ == "__main__":
    brain = TamannaBrain()

    print("=" * 50)
    print("Tamanna AI Brain Core")
    print("=" * 50)

    print(brain.info())
    print(brain.execute("status"))
    print(brain.execute("health"))
    print(brain.execute("save"))
