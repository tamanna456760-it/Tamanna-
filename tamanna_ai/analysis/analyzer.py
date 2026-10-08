"""Project analysis logic."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List


class ProjectAnalyzer:
    def __init__(self, root: str | Path | None = None):
        self.root = Path(root).resolve() if root else Path.cwd()

    def scan(self) -> Dict[str, Any]:
        files = [str(p) for p in self.root.rglob("*") if p.is_file()]
        return {"root": str(self.root), "files": files, "count": len(files)}

    def summarize(self) -> Dict[str, Any]:
        return {"status": "ok", "summary": {"files": self.scan()["count"]}}


project_analyzer = ProjectAnalyzer()

__all__ = ["ProjectAnalyzer", "project_analyzer"]
