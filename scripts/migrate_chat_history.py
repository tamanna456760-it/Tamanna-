#!/usr/bin/env python3
"""Back up and import legacy data/chat_history.json into SQLAlchemy SQLite storage."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tamanna_ai.persistence.database import database, migrate_legacy_json


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    legacy = root / "data" / "chat_history.json"
    database.init()
    result = migrate_legacy_json(legacy)
    print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
