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
class TamannaUnifiedCore:
    def __init__(self):
        self.emotion = "calm"
        self.intel = "idle"
        self.sync_state = "normal"
        self.memory = []

    def log(self, kind, detail):
        entry = {"kind": kind, "detail": detail}
        self.memory.append(entry)
        print("🔗 SyncLog:", entry)

    # ---------- Emotion Layer ----------
    def update_emotion(self, signal):
        mapping = {
            "ok": "calm",
            "warn": "alert",
            "error": "pain",
            "deep": "focused"
        }
        self.emotion = mapping.get(signal, "unknown")
        self.log("emotion", self.emotion)

    # ---------- Intelligence Layer ----------
    def update_intel(self, signal):
        mapping = {
            "ok": "stable",
            "warn": "monitoring",
            "error": "critical",
            "deep": "deep_mode"
        }
        self.intel = mapping.get(signal, "unknown")
        self.log("intelligence", self.intel)

    # ---------- Sync Pulse ----------
    def sync_pulse(self):
        pulse = f"emotion={self.emotion}, intel={self.intel}, mode={self.sync_state}"
        self.log("pulse", pulse)

    # ---------- Unified Sync ----------
    def sync(self, signal):
        self.update_emotion(signal)
        self.update_intel(signal)

        if signal == "deep":
            self.sync_state = "deep_sync"
        elif signal == "error":
            self.sync_state = "defense_sync"
        else:
            self.sync_state = "normal"

        self.log("sync_state", self.sync_state)
        self.sync_pulse()
class TamannaPowerExpansion:
    def __init__(self):
        self.emotion = "calm"
        self.intel = "stable"
        self.sync = "normal"
        self.energy = 1.0   # symbolic power level

    def log(self, kind, detail):
        print("⚡", kind, "→", detail)

    def pulse(self):
        state = f"emotion={self.emotion}, intel={self.intel}, sync={self.sync}, energy={self.energy}"
        self.log("pulse", state)

    def amplify(self):
        self.energy = round(self.energy * 1.2, 2)
        self.log("amplify", f"energy boosted to {self.energy}")

    def shift(self, signal):
        if signal == "deep":
            self.emotion = "focused"
            self.intel = "deep_mode"
            self.sync = "deep_sync"
            self.amplify()

        elif signal == "warn":
            self.emotion = "alert"
            self.intel = "monitoring"
            self.sync = "defense_sync"

        elif signal == "error":
            self.emotion = "pain"
            self.intel = "critical"
            self.sync = "defense_sync"

        else:
            self.emotion = "calm"
            self.intel = "stable"
            self.sync = "normal"

        self.pulse()
