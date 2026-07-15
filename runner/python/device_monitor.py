# device_monitor.py
import datetime
import subprocess


def log(message):
    with open("../logs/device_status.txt", "a") as f:
        f.write(f"{datetime.datetime.now()}: {message}\n")

def ping_device(ip):
    response = subprocess.run(["ping", "-c", "1", ip], capture_output=True)
    if response.returncode == 0:
        log(f"Device {ip} is ONLINE")
    else:
        log(f"Device {ip} is OFFLINE")

# Example device list
devices = ["192.168.1.10", "192.168.1.15", "192.168.1.20"]
for ip in devices:
    ping_device(ip)

print("Device monitoring complete.")