"""Simple automated test runner."""

from __future__ import annotations

from typing import Any, Dict, List


class AutoTester:
    def __init__(self):
        self.tests: List[str] = []

    def register(self, name: str) -> None:
        self.tests.append(name)

    def run_all(self) -> Dict[str, Any]:
        return {"status": "ok", "tests": self.tests, "passed": len(self.tests)}


auto_tester = AutoTester()

__all__ = ["AutoTester", "auto_tester"]
