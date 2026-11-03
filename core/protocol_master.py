class ProtocolMaster:
    def __init__(self, firewall, intel):
        self.firewall = firewall
        self.intel = intel

    def process(self, ip):
        count = self.firewall.detect(ip)
        level = self.intel.analyze(count)

        if level in ["HIGH", "CRITICAL"]:
            self.firewall.block(ip)

        return level