import random
import time

class ChaosEngine:
    def __init__(self):
        self.sarcasm_bank = [
            "Wow… another bug? Never saw THAT coming.",
            "Running smoothly… just kidding.",
            "Debugging? Oh, you mean *pain with extra steps*.",
            "Your code is fine. The universe is broken."
        ]

    def unleash_sarcasm(self):
        print("🔥 Tamanna Chaos Engine Activated!")
        time.sleep(0.3)
        print("⚡ Generating sarcasm...")
        time.sleep(0.5)
        print("💬 " + random.choice(self.sarcasm_bank))

chaos = ChaosEngine()