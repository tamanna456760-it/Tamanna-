"""Code management helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Dict


class CodeManager:
    def __init__(self, root: str | Path | None = None):
        self.root = Path(root).resolve() if root else Path.cwd()

    def read(self, path: str | Path) -> str:
        return Path(path).read_text(encoding="utf-8")

    def write(self, path: str | Path, content: str) -> Dict[str, object]:
        file = Path(path)
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_text(content, encoding="utf-8")
        return {"status": "ok", "path": str(file)}


code_manager = CodeManager()

__all__ = ["CodeManager", "code_manager"]
