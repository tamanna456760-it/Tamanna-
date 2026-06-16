import os
import time
import re
import subprocess
from datetime import datetime

LOG_FILE = "/var/log/auth.log"  # Linux auth log (Ubuntu/Debian)

SUSPICIOUS_PATTERNS = [
    r"Failed password",
    r"Invalid user",
    r"authentication failure",
    r"sudo: .* authentication failure",
    r"Failed publickey"
]

BLOCKED_IPS = set()

def log(msg):
    print(f"[{datetime.now()}] {msg}")

def tail_log(file_path):
    with open(file_path, "r", errors="ignore") as f:
        f.seek(0, os.SEEK_END)
        while True:
            line = f.readline()
            if not line:
                time.sleep(1)
                continue
            yield line

def extract_ip(line):
    match = re.search(r"(\d+\.\d+\.\d+\.\d+)", line)
    return match.group(1) if match else None

def is_suspicious(line):
    return any(re.search(pattern, line) for pattern in SUSPICIOUS_PATTERNS)

def block_ip(ip):
    if ip in BLOCKED_IPS:
        return
    BLOCKED_IPS.add(ip)

    # firewall block (requires sudo)
    cmd = f"iptables -A INPUT -s {ip} -j DROP"
    os.system(cmd)

    log(f"🚨 BLOCKED IP: {ip}")

def analyze_line(line):
    if is_suspicious(line):
        ip = extract_ip(line)
        if ip:
            log(f"⚠ Suspicious activity detected from {ip}")
            block_ip(ip)
        else:
            log("⚠ Suspicious activity detected (no IP found)")

def system_health_check():
    log("🔍 Running system health check...")

    cpu = subprocess.getoutput("top -bn1 | grep 'Cpu'")
    mem = subprocess.getoutput("free -m")

    log(f"CPU INFO: {cpu}")
    log(f"MEM INFO: {mem}")

def main():
    log("🛡 Security Agent Started (DEFENSIVE MODE)")
    system_health_check()

    try:
        for line in tail_log(LOG_FILE):
            analyze_line(line)
    except KeyboardInterrupt:
        log("🛑 Security Agent Stopped")

if __name__ == "__main__":
    main()