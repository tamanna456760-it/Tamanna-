# BD KING R7 Program Engine
class BDKingR7:
    def __init__(self):
        self.modules = []

    def add_module(self, name):
        self.modules.append(name)
        print(f"[BD-KING-R7] Module added: {name}")

    def run(self):
        print("[BD-KING-R7] Running all modules...")
        for m in self.modules:
            print(f" -> {m} active")


if __name__ == "__main__":
    r7 = BDKingR7()
    r7.add_module("Tamanna AI")
    r7.run()
