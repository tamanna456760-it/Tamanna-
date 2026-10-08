"""Backup creation and restore manager."""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any, Dict


class BackupManager:
    def __init__(self, root: str | Path | None = None):
        self.root = Path(root).resolve() if root else Path.cwd()

    def create(self, target: str | Path) -> Dict[str, Any]:
        src = Path(target)
        backup_path = self.root / f"{src.name}.bak"
        if src.exists():
            shutil.copy2(src, backup_path)
        return {"status": "ok", "source": str(src), "backup": str(backup_path)}


backup_manager = BackupManager()

__all__ = ["BackupManager", "backup_manager"]
