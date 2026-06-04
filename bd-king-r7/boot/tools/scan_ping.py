# scan_ping.py
import subprocess
import datetime

def log(message):
    with open("../logs/system_log.txt", "a") as f:
        f.write(f"{datetime.datetime.now()}: {message}\n")

def scan_and_ping():
    devices = subprocess.run(["arp", "-a"], capture_output=True, text=True).stdout.splitlines()
    for device in devices:
        ip = device.split()[0]
        response = subprocess.run(["ping", "-c", "1", ip], capture_output=True)
        if response.returncode == 0:
            log(f"Device {ip} is online.")
        else:
            log(f"Device {ip} is offline or unreachable.")

if __name__ == "__main__":
    scan_and_ping()