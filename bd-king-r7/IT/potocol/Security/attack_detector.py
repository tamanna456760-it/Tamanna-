import time
from collections import defaultdict, deque

class AttackDetector:
    def __init__(self, max_requests=30, window=60):
        # প্রতি IP এর request history
        self.requests = defaultdict(deque)

        # settings
        self.max_requests = max_requests
        self.window = window  # seconds

    def analyze(self, ip):
        now = time.time()

        # পুরানো request clean করা
        q = self.requests[ip]
        while q and now - q[0] > self.window:
            q.popleft()

        # নতুন request add
        q.append(now)

        # threshold check
        if len(q) > self.max_requests:
            return {
                "risk": "HIGH",
                "ip": ip,
                "reason": "Too many requests in short time",
                "count": len(q)
            }

        # light suspicious behavior
        if len(q) > self.max_requests * 0.7:
            return {
                "risk": "MEDIUM",
                "ip": ip,
                "reason": "High traffic detected",
                "count": len(q)
            }

        return {
            "risk": "LOW",
            "ip": ip,
            "count": len(q)
        }