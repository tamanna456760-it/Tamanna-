import json
import logging
import subprocess
import threading
import time

from scapy.all import ARP, sniff

CONFIG_FILE = "config.json"
BLOCK_CACHE = {}
BLOCK_COOLDOWN = 300  # seconds before re-blocking same IP

logging.basicConfig(
    filename="advanced_blocker.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def load_config():
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

config = load_config()
BLACKLIST = set(config["blacklist"])
MAC_MAP = config.get("mac_map", {})  # optional: expected MAC per IP


def run_cmd(cmd):
    try:
        return subprocess.check_output(cmd, shell=True, text=True)
    except Exception as e:
        logging.error(f"Command failed: {cmd} | {e}")
        return ""


def block_ip(ip):
    now = time.time()

    # rate-limit blocking
    if ip in BLOCK_CACHE and now - BLOCK_CACHE[ip] < BLOCK_COOLDOWN:
        return

    logging.warning(f"Blocking IP: {ip}")
    run_cmd(f"sudo ufw deny from {ip}")
    BLOCK_CACHE[ip] = now
    print(f"[BLOCKED] {ip}")


def alert(message):
    """Hook for Telegram/email alerts."""
    logging.warning(f"ALERT: {message}")
    print(f"[ALERT] {message}")
    # Add your Telegram bot or email API here


def handle_arp(pkt):
    if pkt.haslayer(ARP) and pkt[ARP].op == 2:  # ARP reply
        ip = pkt[ARP].psrc
        mac = pkt[ARP].hwsrc

        # 1. Blacklist detection
        if ip in BLACKLIST:
            alert(f"Blacklisted IP detected: {ip} ({mac})")
            block_ip(ip)

        # 2. ARP spoofing detection
        if ip in MAC_MAP:
            expected_mac = MAC_MAP[ip]
            if mac.lower() != expected_mac.lower():
                alert(f"ARP SPOOFING detected! IP {ip} changed MAC {mac} != {expected_mac}")
                block_ip(ip)


def start_sniffer():
    sniff(filter="arp", store=False, prn=handle_arp)


def main():
    print("Starting advanced ARP intrusion monitor...")
    logging.info("System started")

    sniffer_thread = threading.Thread(target=start_sniffer)
    sniffer_thread.daemon = True
    sniffer_thread.start()

    while True:
        time.sleep(1)


if __name__ == "__main__":
    main()