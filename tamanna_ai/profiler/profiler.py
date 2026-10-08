"""Performance profiler."""

from __future__ import annotations

from time import perf_counter
from typing import Dict


class Profiler:
    def __init__(self):
        self.samples = []

    def measure(self, label: str, fn):
        start = perf_counter()
        result = fn()
        elapsed = perf_counter() - start
        self.samples.append({"label": label, "elapsed": elapsed})
        return result

    def summary(self) -> Dict[str, float]:
        return {"total_samples": len(self.samples), "avg_elapsed": sum(item["elapsed"] for item in self.samples) / max(1, len(self.samples))}


profiler = Profiler()

__all__ = ["Profiler", "profiler"]
