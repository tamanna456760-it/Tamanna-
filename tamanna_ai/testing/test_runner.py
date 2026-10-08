"""Test runner helper."""

from __future__ import annotations

from typing import Any, Dict, List


class TestRunner:
    def __init__(self):
        self.tests: List[str] = []

    def add(self, name: str) -> None:
        self.tests.append(name)

    def run(self) -> Dict[str, Any]:
        return {"status": "ok", "tests": self.tests, "passed": len(self.tests)}


test_runner = TestRunner()

__all__ = ["TestRunner", "test_runner"]
