import time
from collections import defaultdict
import requests


class FirewallCore:
    def __init__(self, node_url):
        self.logs = defaultdict(list)
        self.blocked = set()
        self.node_url = node_url

    def log(self, ip):
        now = time.time()
        self.logs[ip].append(now)

        # keep last 60 sec
        self.logs[ip] = [t for t in self.logs[ip] if now - t < 60]

    def detect(self, ip):
        return len(self.logs[ip])

    def block(self, ip):
        if ip in self.blocked:
            return

        self.blocked.add(ip)

        # send to node server
        requests.post(f"{self.node_url}/block", json={"ip": ip})
        print("[PYTHON] BLOCKED:", ip)
