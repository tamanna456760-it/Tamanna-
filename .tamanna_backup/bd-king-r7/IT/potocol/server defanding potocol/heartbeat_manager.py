import time


class HeartbeatManager:
    def __init__(self):
        self.nodes = {}

    def update(self, node):
        self.nodes[node] = time.time()

    def online_nodes(self, timeout=60):
        now = time.time()
        return [n for n, t in self.nodes.items() if now - t < timeout]
