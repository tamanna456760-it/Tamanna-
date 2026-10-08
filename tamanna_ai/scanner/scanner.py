"""Repository scanner."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List


class RepoScanner:
    def __init__(self, root: str | Path | None = None):
        self.root = Path(root).resolve() if root else Path.cwd()

    def walk(self) -> List[str]:
        return [str(p) for p in self.root.rglob("*") if p.is_file()]

    def scan(self) -> Dict[str, Any]:
        files = self.walk()
        return {"status": "ok", "files": files, "count": len(files)}


repo_scanner = RepoScanner()

__all__ = ["RepoScanner", "repo_scanner"]
