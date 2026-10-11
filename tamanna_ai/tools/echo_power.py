#!/usr/bin/env python3

from datetime import datetime
import platform
import sys

def tamanna_echo(message):
    return f"Tamanna AI: {message}"

def power_status():
    return {
        "name": "Tamanna AI",
        "status": "ONLINE",
        "system": platform.system(),
        "python": platform.python_version(),
        "time": datetime.now().isoformat(timespec="seconds"),
    }

if __name__ == "__main__":
    print("===== TAMANNA AI ECHO POWER =====")
    print(tamanna_echo("Echo engine is working!"))
    for key, value in power_status().items():
        print(f"{key}: {value}")
