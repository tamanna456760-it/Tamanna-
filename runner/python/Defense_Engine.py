import time
from collections import defaultdict


class TamannaDefenseProtocol:
    def __init__(self, config):
        self.config = config
        self.request_log = defaultdict(list)
        self.blocked_ips = set()

    def log_request(self, ip):
        now = time.time()
        self.request_log[ip].append(now)

        # remove old requests (>60 sec)
        self.request_log[ip] = [
            t for t in self.request_log[ip]
            if now - t < 60
        ]

    def is_attack(self, ip):
        if ip in self.blocked_ips:
            return True

        requests = len(self.request_log[ip])

        if requests > self.config["block_threshold"]:
            self.block_ip(ip)
            return True

        return False

    def block_ip(self, ip):
        self.blocked_ips.add(ip)
        print(f"[DEFENSE] BLOCKED IP: {ip}")

    def monitor(self, ip):
        self.log_request(ip)

        if len(self.request_log[ip]) > self.config["max_requests_per_minute"]:
            self.block_ip(ip)
            return "blocked"

        return "safe"