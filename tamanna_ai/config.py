"""Project-wide configuration for Tamanna AI."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict


@dataclass
class Settings:
    project_root: Path = field(default_factory=lambda: Path(__file__).resolve().parent.parent)
    app_name: str = "Tamanna AI"
    version: str = "1.0.0"
    debug: bool = True
    environment: str = "development"
    extra: Dict[str, Any] = field(default_factory=dict)


settings = Settings()

__all__ = ["Settings", "settings"]
