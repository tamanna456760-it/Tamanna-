import random
import time
from collections import defaultdict


class AdaptiveDefenseCore:
    def __init__(self, config):
        self.config = config
        self.traffic = defaultdict(list)
        self.blocked = set()
        self.threat_score = defaultdict(float)

    # 📡 request log
    def log(self, ip):
        now = time.time()
        self.traffic[ip].append(now)

        # keep last 60 sec data
        self.traffic[ip] = [t for t in self.traffic[ip] if now - t < 60]

    # 🧠 threat analysis
    def analyze(self, ip):
        count = len(self.traffic[ip])

        score = count / 100
        self.threat_score[ip] = min(1.0, score)

        return score

    # 🛡️ defense action
    def defend(self, ip):
        score = self.analyze(ip)

        if score > self.config["risk_threshold"]:
            self.block(ip)
            return "BLOCKED"

        return "SAFE"

    # 🚫 block system
    def block(self, ip):
        self.blocked.add(ip)
        print(f"[DEFENSE] BLOCKED IP -> {ip}")

    # 🔄 auto learning upgrade
    def learn(self):
        for ip, score in self.threat_score.items():
            if score > 0.5:
                self.threat_score[ip] *= 0.95  # adapt sensitivity

    # ⚡ self upgrade trigger
    def auto_upgrade(self):
        if len(self.blocked) > 10:
            self.config["risk_threshold"] = max(0.5, self.config["risk_threshold"] - 0.05)
            print("[UPGRADE] Defense sensitivity increased")