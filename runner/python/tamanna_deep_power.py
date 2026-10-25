
class TamannaDeepPower:
    def __init__(self):
        self.state = "calm"
        self.memory = []
        self.energy = 1.0

    def boost_energy(self, pressure):
        """Increase the symbolic energy level."""
        try:
            amount = float(pressure)
        except (TypeError, ValueError):
            raise ValueError("pressure must be a number") from None

        self.energy = round(self.energy + (amount * 0.1), 2)
        self.log("energy_boost", f"Energy now {self.energy}")
        return self.energy

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
