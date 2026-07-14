import time


class RateLimiter:
    def __init__(self, limit=30):
        self.limit = limit
        self.requests = {}

    def allow(self, ip):
        now = time.time()

        self.requests.setdefault(ip, [])
        self.requests[ip] = [t for t in self.requests[ip] if now - t < 60]

        if len(self.requests[ip]) >= self.limit:
            return False

        self.requests[ip].append(now)
        return True
