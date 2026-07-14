import time
from collections import defaultdict


class TamannaGlobalFirewall:
    def __init__(self, config):
        self.config = config
        self.ip_logs = defaultdict(list)
        self.blocked_ips = set()
        self.server_nodes = []

    # 🌐 register servers
    def register_node(self, node):
        self.server_nodes.append(node)

    # 📡 log traffic
    def log_request(self, ip):
        now = time.time()
        self.ip_logs[ip].append(now)

        # keep last 60 sec
        self.ip_logs[ip] = [t for t in self.ip_logs[ip] if now - t < 60]

    # 🧠 detect attack
    def detect(self, ip):
        count = len(self.ip_logs[ip])

        if count > self.config["global_block_threshold"]:
            self.block(ip)
            return "GLOBAL_BLOCK"

        elif count > self.config["max_rpm_per_ip"]:
            return "SUSPICIOUS"

        return "SAFE"

    # 🚫 block across all servers
    def block(self, ip):
        self.blocked_ips.add(ip)

        for node in self.server_nodes:
            node.block_ip(ip)

        print(f"[GLOBAL FIREWALL] BLOCKED IP: {ip}")

    # 🔄 sync rules across servers
    def sync_rules(self):
        for node in self.server_nodes:
            node.update_rules(self.config)

        print("[SYNC] Firewall rules synced to all nodes")
