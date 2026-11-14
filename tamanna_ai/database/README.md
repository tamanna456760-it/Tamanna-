# Database package boundary

The current SQLAlchemy database implementation lives in `tamanna_ai/persistence/` (including its `database.py` module and public exports).

This directory is a documented target boundary only. Do not add a second database engine, session manager, model set, or migration system here. A future consolidation may move the implementation into this package only after all imports, tests, migrations, and runtime entrypoints are updated together.

For now, import the established implementation from `tamanna_ai.persistence`.
