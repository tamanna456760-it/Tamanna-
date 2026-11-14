"""Small dependency-free timing collector for local performance checks."""
from __future__ import annotations

from contextlib import contextmanager
from statistics import mean
from time import perf_counter
from typing import Iterator


class PerformanceMonitor:
    def __init__(self, max_samples: int = 1000) -> None:
        if max_samples < 1:
            raise ValueError("max_samples must be positive")
        self.max_samples = int(max_samples)
        self.samples: list[dict[str, float | str]] = []

    def record(self, label: str, elapsed_seconds: float) -> None:
        elapsed = float(elapsed_seconds)
        if elapsed < 0:
            raise ValueError("elapsed_seconds cannot be negative")
        self.samples.append({"label": str(label), "elapsed_seconds": elapsed})
        if len(self.samples) > self.max_samples:
            del self.samples[: len(self.samples) - self.max_samples]

    @contextmanager
    def measure(self, label: str) -> Iterator[None]:
        start = perf_counter()
        try:
            yield
        finally:
            self.record(label, perf_counter() - start)

    def summary(self) -> dict[str, float | int]:
        values = [float(row["elapsed_seconds"]) for row in self.samples]
        return {
            "samples": len(values),
            "total_seconds": sum(values),
            "average_seconds": mean(values) if values else 0.0,
            "max_seconds": max(values, default=0.0),
        }

    def clear(self) -> None:
        self.samples.clear()


__all__ = ["PerformanceMonitor"]
