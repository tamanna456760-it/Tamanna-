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


def test_sqlite_backup_preserves_knowledge_records(tmp_path):
    database_path = tmp_path / "live.sqlite3"
    backup_path = tmp_path / "backups" / "tamanna-backup.sqlite3"
    database = Database(f"sqlite:///{database_path}")
    database.init()
    owner_id = database.ensure_user("backup-owner@example.test", "Backup Owner")

    with database.Session.begin() as session:
        session.add(
            Memory(
                user_id=owner_id,
                content="backup verification record",
                metadata_json='{"kind":"test"}',
            )
        )

    created_backup = database.backup_to(backup_path)
    assert created_backup == backup_path.resolve()
    assert created_backup.is_file()

    backup_database = Database(f"sqlite:///{created_backup}")
    with backup_database.Session() as session:
        restored = session.query(Memory).filter_by(
            content="backup verification record"
        ).one()
        assert restored.user_id == owner_id


def test_sqlite_backup_refuses_to_overwrite_existing_file(tmp_path):
    database = Database(f"sqlite:///{tmp_path / 'live.sqlite3'}")
    database.init()
    destination = tmp_path / "existing-backup.sqlite3"
    destination.write_text("keep existing file", encoding="utf-8")

    import pytest

    with pytest.raises(FileExistsError):
        database.backup_to(destination)

    assert destination.read_text(encoding="utf-8") == "keep existing file"


def test_sqlite_backup_rejects_live_database_as_destination(tmp_path):
    database_path = tmp_path / "live.sqlite3"
    database = Database(f"sqlite:///{database_path}")
    database.init()

    import pytest

    with pytest.raises(ValueError, match="differ"):
        database.backup_to(database_path)


def test_restore_backup_creates_separate_database_with_knowledge(tmp_path):
    live_path = tmp_path / "live.sqlite3"
    backup_path = tmp_path / "backup.sqlite3"
    restore_path = tmp_path / "recovered" / "restored.sqlite3"
    database = Database(f"sqlite:///{live_path}")
    database.init()
    owner_id = database.ensure_user("restore-owner@example.test", "Restore Owner")

    with database.Session.begin() as session:
        session.add(
            Memory(
                user_id=owner_id,
                content="recoverable knowledge",
                metadata_json='{"source":"restore-test"}',
            )
        )

    database.backup_to(backup_path)
    restored_path = Database.restore_backup_to(backup_path, restore_path)
    assert restored_path == restore_path.resolve()

    recovered = Database(f"sqlite:///{restored_path}")
    with recovered.Session() as session:
        record = session.query(Memory).filter_by(
            content="recoverable knowledge"
        ).one()
        assert record.user_id == owner_id


def test_restore_refuses_to_overwrite_existing_destination(tmp_path):
    backup_database = Database(f"sqlite:///{tmp_path / 'backup-source.sqlite3'}")
    backup_database.init()
    backup_path = backup_database.backup_to(tmp_path / "backup.sqlite3")
    destination = tmp_path / "existing.sqlite3"
    destination.write_text("preserve this file", encoding="utf-8")

    import pytest

    with pytest.raises(FileExistsError):
        Database.restore_backup_to(backup_path, destination)

    assert destination.read_text(encoding="utf-8") == "preserve this file"


def test_restore_rejects_corrupt_backup(tmp_path):
    corrupt_backup = tmp_path / "corrupt.sqlite3"
    corrupt_backup.write_bytes(b"not a sqlite database")
    destination = tmp_path / "restored.sqlite3"

    import pytest

    with pytest.raises(Exception):
        Database.restore_backup_to(corrupt_backup, destination)

    assert not destination.exists()


def test_backup_initializes_schema_and_handles_spaces_in_paths(tmp_path):
    live_path = tmp_path / "live database.sqlite3"
    backup_path = tmp_path / "backup folder" / "safe backup.sqlite3"
    database = Database(f"sqlite:///{live_path}")

    created = database.backup_to(backup_path)
    assert created.is_file()

    restored_path = Database.restore_backup_to(
        created, tmp_path / "restored folder" / "restored database.sqlite3"
    )
    restored = Database(f"sqlite:///{restored_path}")
    assert restored.ping()
    with restored.Session() as session:
        assert session.query(Memory).count() == 0
