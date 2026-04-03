# Defensive security tools
import logging


class NetworkDefender:
    def __init__(self):
        self.suspicious_activities = []
        self.setup_logging()

    def setup_logging(self):
        """Setup security event logging"""
        logging.basicConfig(
            filename="security_events.log",
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
        )

    def monitor_connections(self):
        """Monitor network connections (defensive)"""
        # This is for monitoring YOUR OWN systems
        pass

    def detect_intrusion_attempts(self, log_data):
        """Analyze logs for intrusion attempts"""
        suspicious_patterns = [
            "failed password",
            "authentication failure",
            "port scan",
            "brute force attempt",
        ]

        detected_threats = []
        for pattern in suspicious_patterns:
            if pattern in log_data.lower():
                detected_threats.append(pattern)
                logging.warning(f"Detected suspicious activity: {pattern}")

        return detected_threats
