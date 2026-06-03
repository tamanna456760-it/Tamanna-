class FirewallAI:
    def evolve(self, firewall):
        avg_attack = len(firewall.blocked_ips)

        if avg_attack > 50:
            firewall.config["global_block_threshold"] -= 10
            print("[AI] Firewall sensitivity increased")

        elif avg_attack < 10:
            firewall.config["global_block_threshold"] += 5
            print("[AI] Firewall relaxed safely")