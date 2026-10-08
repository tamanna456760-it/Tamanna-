"""Static code analyzer."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List


class CodeAnalyzer:
    def __init__(self, root: str | Path | None = None):
        self.root = Path(root).resolve() if root else Path.cwd()

    def find_python_files(self) -> List[str]:
        return [str(p) for p in self.root.rglob("*.py")]

    def analyze(self) -> Dict[str, object]:
        files = self.find_python_files()
        return {"status": "ok", "files": files, "count": len(files)}


code_analyzer = CodeAnalyzer()

__all__ = ["CodeAnalyzer", "code_analyzer"]
