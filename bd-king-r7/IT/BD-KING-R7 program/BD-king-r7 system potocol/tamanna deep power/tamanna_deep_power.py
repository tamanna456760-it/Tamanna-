class TamannaDeepPower:
    def __init__(self):
        self.state = "calm"
        self.memory = []

    def log(self, event, detail):
        entry = {"event": event, "detail": detail}
        self.memory.append(entry)
        print("📘 Memory:", entry)

    def set_state(self, new_state):
        self.state = new_state
        self.log("state_change", new_state)

    def heartbeat(self):
        self.log("heartbeat", f"State: {self.state}")

    def react(self, signal):
        if signal == "ok":
            self.set_state("calm")
        elif signal == "warn":
            self.set_state("alert")
        elif signal == "error":
            self.set_state("pain")
        elif signal == "recover":
            self.set_state("healing")
        else:
            self.set_state("unknown")
class SyncPower:
    def __init__(self):
        self.emotion = "calm"
        self.intel_state = "idle"
        self.memory = []

    def log(self, kind, detail):
        entry = {"kind": kind, "detail": detail}
        self.memory.append(entry)
        print("🔗 SyncLog:", entry)

    def heartbeat(self):
        self.log("heartbeat", f"emotion={self.emotion}, intel={self.intel_state}")

    def sync_emotion(self, signal):
        mapping = {
            "ok": "calm",
            "warn": "alert",
            "error": "pain",
            "deep": "focused"
        }
        self.emotion = mapping.get(signal, "unknown")
        self.log("emotion_update", self.emotion)

    def sync_intelligence(self, signal):
        mapping = {
            "ok": "stable",
            "warn": "monitoring",
            "error": "critical",
            "deep": "deep_mode"
        }
        self.intel_state = mapping.get(signal, "unknown")
        self.log("intel_update", self.intel_state)

    def sync(self, signal):
        self.sync_emotion(signal)
        self.sync_intelligence(signal)
        self.heartbeat()
