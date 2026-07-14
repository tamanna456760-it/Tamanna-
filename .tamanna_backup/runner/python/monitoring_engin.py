# Tamanna Monitoring Engine
import time


class MonitoringEngine:
    def __init__(self):
        self.status = {}

    def log(self, module, state: bool):
        self.status[module] = state
        print(f"[MONITOR] {module} => {'TRUE' if state else 'FALSE'}")

    def heartbeat(self):
        while True:
            print("[HEARTBEAT] System alive...")
            time.sleep(5)


if __name__ == "__main__":
    monitor = MonitoringEngine()
    monitor.log("TamannaCore", True)
    monitor.heartbeat()
