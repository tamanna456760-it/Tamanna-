"""Git operations helper."""

from __future__ import annotations

from typing import Dict


class GitManager:
    def status(self) -> Dict[str, object]:
        return {"status": "ok", "branch": "main", "clean": True}


git_manager = GitManager()

__all__ = ["GitManager", "git_manager"]
