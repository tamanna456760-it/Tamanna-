import os
import socket
import subprocess
import time

# -------------------------
# Tamanna System Settings
# -------------------------
SYSTEM_NAME = "TAMANNA SYSTEM"
CHECK_HOST = "google.com"
SLEEP_TIME = 10  # seconds
AUTO_MODE = True


# -------------------------
# Network Check (Safe)
# -------------------------
def check_network(host):
    try:
        socket.gethostbyname(host)
        return True
    except:
        return False


# -------------------------
# Ping Style Check (OS)
# -------------------------
def ping(host):
    """Run one bounded ping without invoking a command shell."""
    if not isinstance(host, str) or not host or any(ch.isspace() for ch in host):
        return False
    command = ["ping", "-n", "1", host] if os.name == "nt" else ["ping", "-c", "1", host]
    try:
        result = subprocess.run(
            command,
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=5,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False
    return result.returncode == 0


# -------------------------
# Sleep Mode
# -------------------------
def sleep_mode():
    print("😴 Tamanna System is now in SLEEP MODE")
    time.sleep(SLEEP_TIME)
    print("⚡ Tamanna System waking up...")


# -------------------------
# Main System Loop
# -------------------------
def start_system():
    print("🚀 Starting", SYSTEM_NAME)
    print("-" * 30)

    while AUTO_MODE:
        net = check_network(CHECK_HOST)
        ping_status = ping(CHECK_HOST)

        print("📡 Network:", "CONNECTED ✅" if net else "DISCONNECTED ❌")
        print("📶 Ping:", "OK ✅" if ping_status else "FAILED ❌")
        print("🔁 Auto Mode: ON")

        sleep_mode()
        print("-" * 30)


# -------------------------
# Run System
# -------------------------
if __name__ == "__main__":
    start_system()