from __future__ import annotations

from sqlalchemy import inspect

from tamanna_ai.persistence.database import Database


def test_memory_table_has_composite_owner_and_id_index(tmp_path):
    database = Database(f"sqlite:///{tmp_path / 'knowledge-index.sqlite3'}")
    database.init()

    indexes = inspect(database.engine).get_indexes("memories")
    indexed_columns = {
        tuple(index["column_names"])
        for index in indexes
    }

    assert ("user_id", "id") in indexed_columns
