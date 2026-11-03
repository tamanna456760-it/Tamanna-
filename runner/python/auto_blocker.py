import json
import subprocess
import ipaddress
import shlex
import threading
import time
from datetime import datetime

from scapy.all import ARP, sniff

BLACKLIST = {
    "192.168.1.100": "AA:BB:CC:DD:EE:FF",  # IP : Expected MAC
}

BLOCKED_FILE = "blocked_ips.json"
RATE_LIMIT_SECONDS = 60  # avoid re-blocking too often


def load_blocked():
    try:
        with open(BLOCKED_FILE, "r") as f:
            return json.load(f)
    except:
        return {}


def save_blocked(data):
    with open(BLOCKED_FILE, "w") as f:
        json.dump(data, f, indent=4)


BLOCKED_CACHE = load_blocked()


def log(msg, level="INFO"):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] [{level}] {msg}")


def run_cmd(cmd):
    try:
        args = shlex.split(cmd)
        if not args or args[0] != "sudo" or args[1:3] != ["ufw", "deny"]:
            raise ValueError("command not allowed")
        subprocess.run(args, shell=False, check=True, timeout=10)
    except Exception as e:
        log(f"Firewall command failed: {type(e).__name__}", "ERROR")


def block_ip(ip):
    try:
        ip = str(ipaddress.ip_address(ip))
    except ValueError:
        log("Refusing invalid IP address", "ERROR")
        return
    now = time.time()

    # rate limit
    if ip in BLOCKED_CACHE and now - BLOCKED_CACHE[ip] < RATE_LIMIT_SECONDS:
        return

    log(f"Blocking IP: {ip}", "WARNING")
    run_cmd(f"sudo ufw deny from {ip}")

    BLOCKED_CACHE[ip] = now
    save_blocked(BLOCKED_CACHE)

    log(f"IP {ip} has been blocked", "CRITICAL")


def alert(ip, mac):
    # Placeholder for email/telegram/webhook alerts
    log(f"ALERT: Suspicious device detected → {ip} ({mac})", "ALERT")


def handle_arp(pkt):
    if ARP in pkt and pkt[ARP].op == 2:  # ARP reply
        ip = pkt[ARP].psrc
        mac = pkt[ARP].hwsrc

        if ip in BLACKLIST:
            expected_mac = BLACKLIST[ip]

            if mac.lower() != expected_mac.lower():
                log(f"MAC mismatch for {ip}! Possible spoofing. Got {mac}, expected {expected_mac}", "CRITICAL")
                alert(ip, mac)
                block_ip(ip)
            else:
                log(f"Blacklisted IP detected: {ip} ({mac})", "WARNING")
                block_ip(ip)


def start_sniffer():
    log("Starting real-time ARP monitor...")
    sniff(filter="arp", store=False, prn=handle_arp)


def main():
    t = threading.Thread(target=start_sniffer)
    t.daemon = True
    t.start()

    while True:
        time.sleep(1)


if __name__ == "__main__":
    main()