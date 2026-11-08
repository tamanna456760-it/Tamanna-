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


def test_init_adds_index_to_existing_legacy_memory_table(tmp_path):
    database = Database(f"sqlite:///{tmp_path / 'legacy-knowledge.sqlite3'}")

    # Simulate a database created before the composite index was introduced.
    with database.engine.begin() as connection:
        connection.exec_driver_sql(
            """
            CREATE TABLE memories (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                conversation_id VARCHAR(64),
                content TEXT NOT NULL,
                metadata_json TEXT NOT NULL,
                created_at DATETIME NOT NULL
            )
            """
        )
        connection.exec_driver_sql(
            """
            INSERT INTO memories
                (id, user_id, conversation_id, content, metadata_json, created_at)
            VALUES (41, NULL, NULL, 'legacy knowledge', '{}', '2026-01-01 00:00:00')
            """
        )

    # Repeated startup must remain safe and must not rewrite existing records.
    database.init()
    database.init()

    with database.engine.connect() as connection:
        preserved = connection.exec_driver_sql(
            "SELECT id, content FROM memories WHERE id = 41"
        ).one()
    assert preserved == (41, "legacy knowledge")

    indexes = inspect(database.engine).get_indexes("memories")
    indexed_columns = {
        tuple(index["column_names"])
        for index in indexes
    }
    assert ("user_id", "id") in indexed_columns
