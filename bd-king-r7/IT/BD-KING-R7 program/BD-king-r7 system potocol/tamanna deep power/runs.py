class TamannaDeepPowerV2:
    def __init__(self):
        self.state = "calm"
        self.memory = []

    def log(self, event, detail):
        entry = {"event": event, "detail": detail}
        self.memory.append(entry)
        print("📘", entry)

    def set_state(self, new_state):
        self.state = new_state
        self.log("state_change", new_state)

    def heartbeat(self):
        self.log("heartbeat", f"State: {self.state}")

    def deep_mode(self):
        self.set_state("deep")
        self.log("deep_entry", "Entering deep power mode")

    def react(self, signal):
        mapping = {
            "ok": "calm",
            "warn": "alert",
            "error": "pain",
            "recover": "healing",
            "deep": "deep"
        }
        self.set_state(mapping.get(signal, "unknown"))
