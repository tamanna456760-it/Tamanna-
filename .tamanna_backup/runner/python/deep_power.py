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
