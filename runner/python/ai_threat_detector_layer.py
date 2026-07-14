class AIThreatDetector:
    def detect_spike(self, traffic_data):
        avg = sum(traffic_data) / len(traffic_data)

        if max(traffic_data) > avg * 3:
            return "attack_detected"

        return "normal"

    def classify(self, ip_activity):
        if len(ip_activity) > 200:
            return "DDoS Risk"
        elif len(ip_activity) > 80:
            return "Suspicious"
        return "Safe"
