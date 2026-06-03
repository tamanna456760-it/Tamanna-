class ProtocolController:
    def __init__(self, firewall):
        self.firewall = firewall

    def enforce_protocol(self):
        print("[PROTOCOL] Enforcing global security rules...")

        self.firewall.sync_rules()

    def emergency_lockdown(self):
        print("[EMERGENCY] Locking all traffic...")

        for ip in list(self.firewall.ip_logs.keys()):
            self.firewall.block(ip)