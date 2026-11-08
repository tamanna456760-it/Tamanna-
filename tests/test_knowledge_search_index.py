from __future__ import annotations

from sqlalchemy import inspect

from tamanna_ai.persistence.database import Database, Memory


def test_memory_table_has_composite_owner_and_id_index(tmp_path):
    database = Database(f"sqlite:///{tmp_path / 'knowledge-index.sqlite3'}")
    database.init()

    indexes = inspect(database.engine).get_indexes("memories")
    indexed_columns = {
        tuple(index["column_names"])
        for index in indexes
    }

    assert ("user_id", "id") in indexed_columns


def test_owner_scoped_ordered_memory_query_uses_composite_index(tmp_path):
    database = Database(f"sqlite:///{tmp_path / 'knowledge-query-plan.sqlite3'}")
    database.init()
    owner_id = database.ensure_user("index-owner@example.test", "Index Owner")
    other_id = database.ensure_user("other-owner@example.test", "Other Owner")

    with database.Session.begin() as session:
        session.add_all(
            Memory(
                user_id=owner_id if index % 2 == 0 else other_id,
                content=f"Knowledge record {index}",
                metadata_json='{"kind":"imported_knowledge"}',
            )
            for index in range(1000)
        )

    with database.engine.begin() as connection:
        connection.exec_driver_sql("ANALYZE")
        plan = connection.exec_driver_sql(
            "EXPLAIN QUERY PLAN "
            "SELECT * FROM memories WHERE user_id = ? ORDER BY id",
            (owner_id,),
        ).all()

    plan_text = " ".join(str(row[-1]) for row in plan)
    assert "ix_memories_user_id_id" in plan_text
