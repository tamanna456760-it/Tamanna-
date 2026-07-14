class SecurityUpdater:
    def __init__(self, defense_core):
        self.core = defense_core

    def check_system_health(self):
        if len(self.core.blocked) > 20:
            return "upgrade_needed"
        return "stable"

    def upgrade(self):
        print("[SYSTEM] Upgrading defense engine...")

        # increase sensitivity
        self.core.config["risk_threshold"] *= 0.9

        # clear weak noise
        self.core.traffic.clear()

        print("[SYSTEM] Upgrade complete - Defense stronger now")
