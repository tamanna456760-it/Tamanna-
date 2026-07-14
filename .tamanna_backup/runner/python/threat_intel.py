class ThreatIntel:
    def analyze(self, request_count):
        if request_count > 200:
            return "CRITICAL"
        elif request_count > 100:
            return "HIGH"
        elif request_count > 50:
            return "MEDIUM"
        return "LOW"
