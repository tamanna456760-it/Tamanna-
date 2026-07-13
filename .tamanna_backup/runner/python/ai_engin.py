# AI Monitoring Engine
class AIMonitor:
    def analyze(self, data):
        print(f"[AI MONITOR] Analyzing: {data}")
        return "OK" if "Tamanna" in data else "Alert"

if __name__ == "__main__":
    monitor = AIMonitor()
    print(monitor.analyze("Tamanna AI running"))
