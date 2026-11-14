
"""
Tamanna AI — Advanced API Rate Limiter
Owner: HM INSAN ALI

Provides thread-safe, in-memory request rate limiting.
This is an application-level control, not a network firewall.

Production deployments with multiple workers should use a
shared rate-limit store such as Redis.
"""

from __future__ import annotations

import threading
import time
from collections import defaultdict, deque
from dataclasses import dataclass
from typing import Hashable


@dataclass(frozen=True)
class RateLimitResult:
    allowed: bool
    limit: int
    remaining: int
    retry_after_seconds: float
    reason: str


class RateLimiter:
    """Sliding-window request limiter with bounded client storage."""

    def __init__(
        self,
        requests_per_minute: int = 60,
        burst_limit: int = 10,
        window_seconds: int = 60,
        max_clients: int = 10000,
    ) -> None:
        for name, value in (
            ("requests_per_minute", requests_per_minute),
            ("burst_limit", burst_limit),
            ("window_seconds", window_seconds),
            ("max_clients", max_clients),
        ):
            if type(value) is not int or value < 1:
                raise ValueError(f"{name} must be a positive integer.")

        self.requests_per_minute = requests_per_minute
        self.burst_limit = burst_limit
        self.window_seconds = window_seconds
        self.max_clients = max_clients

        self._requests: dict[Hashable, deque[float]] = defaultdict(deque)
        self._lock = threading.Lock()

    def check(
        self,
        client_id: Hashable,
        now: float | None = None,
    ) -> RateLimitResult:
        """
        Evaluate one request.

        Use a trusted authenticated identity when available.
        Do not accept an arbitrary client identity directly from a
        request header controlled by the caller.
        """
        if not isinstance(client_id, Hashable):
            return RateLimitResult(
                False, self.requests_per_minute, 0, 0.0,
                "invalid_client_id",
            )

        if isinstance(client_id, str) and not client_id.strip():
            return RateLimitResult(
                False, self.requests_per_minute, 0, 0.0,
                "invalid_client_id",
            )

        current = time.monotonic() if now is None else now

        with self._lock:
            if client_id not in self._requests:
                # Avoid unbounded memory growth from arbitrary client IDs.
                if len(self._requests) >= self.max_clients:
                    return RateLimitResult(
                        False, self.requests_per_minute, 0, 1.0,
                        "client_capacity_reached",
                    )

                self._requests[client_id] = deque()

            timestamps = self._requests[client_id]
            cutoff = current - self.window_seconds

            while timestamps and timestamps[0] <= cutoff:
                timestamps.popleft()

            if len(timestamps) >= self.requests_per_minute:
                retry_after = max(
                    0.0,
                    timestamps[0] + self.window_seconds - current,
                )
                return RateLimitResult(
                    False,
                    self.requests_per_minute,
                    0,
                    retry_after,
                    "rate_limit_exceeded",
                )

            # The burst cap prevents a large instantaneous request spike.
            burst_cutoff = current - 1.0
            recent_burst = sum(
                timestamp > burst_cutoff
                for timestamp in timestamps
            )

            if recent_burst >= self.burst_limit:
                oldest_burst = next(
                    (
                        timestamp
                        for timestamp in timestamps
                        if timestamp > burst_cutoff
                    ),
                    current,
                )
                retry_after = max(
                    0.0,
                    oldest_burst + 1.0 - current,
                )
                return RateLimitResult(
                    False,
                    self.requests_per_minute,
                    max(
                        0,
                        self.requests_per_minute - len(timestamps),
                    ),
                    retry_after,
                    "burst_limit_exceeded",
                )

            timestamps.append(current)

            return RateLimitResult(
                True,
                self.requests_per_minute,
                max(
                    0,
                    self.requests_per_minute - len(timestamps),
                ),
                0.0,
                "allowed",
            )

    def reset_client(self, client_id: Hashable) -> bool:
        """Clear one client's counters; call only from trusted code."""
        with self._lock:
            return self._requests.pop(client_id, None) is not None

    def clear(self) -> None:
        """Clear all in-memory counters."""
        with self._lock:
            self._requests.clear()


_DEFAULT_LIMITER = RateLimiter()


def check_request(
    client_id: Hashable,
) -> dict[str, object]:
    """Convenience function using the default limiter."""
    result = _DEFAULT_LIMITER.check(client_id)

    return {
        "allowed": result.allowed,
        "limit": result.limit,
        "remaining": result.remaining,
        "retry_after_seconds": round(
            result.retry_after_seconds, 3
        ),
        "reason": result.reason,
    }


if __name__ == "__main__":
    limiter = RateLimiter(
        requests_per_minute=5,
        burst_limit=2,
        window_seconds=60,
    )

    for number in range(4):
        result = limiter.check("local-test-client", now=100.0)
        print(
            f"Request {number + 1}: "
            f"allowed={result.allowed}, reason={result.reason}"
        )
