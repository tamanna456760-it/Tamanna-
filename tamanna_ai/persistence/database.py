"""SQLAlchemy persistence for users, conversations, messages, and memories."""
from __future__ import annotations

import json
import os
import shutil
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text, create_engine, event, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str | None] = mapped_column(String(254), unique=True, nullable=True)
    name: Mapped[str | None] = mapped_column(String(80), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class Conversation(Base):
    __tablename__ = "conversations"
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    title: Mapped[str] = mapped_column(String(200), default="New conversation")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    messages: Mapped[list["Message"]] = relationship(
        back_populates="conversation", cascade="all, delete-orphan",
        order_by="Message.created_at",
    )


class Message(Base):
    __tablename__ = "messages"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    conversation_id: Mapped[str] = mapped_column(
        ForeignKey("conversations.id", ondelete="CASCADE"), index=True
    )
    role: Mapped[str] = mapped_column(String(16))
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    legacy_key: Mapped[str | None] = mapped_column(String(128), unique=True, nullable=True)
    conversation: Mapped[Conversation] = relationship(back_populates="messages")


class Memory(Base):
    __tablename__ = "memories"
    __table_args__ = (Index("ix_memories_user_id_id", "user_id", "id"),)
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    conversation_id: Mapped[str | None] = mapped_column(
        ForeignKey("conversations.id", ondelete="SET NULL"), nullable=True
    )
    content: Mapped[str] = mapped_column(Text)
    metadata_json: Mapped[str] = mapped_column(Text, default="{}")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class UserSettings(Base):
    """One private profile/settings record per user."""
    __tablename__ = "user_settings"
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    language: Mapped[str] = mapped_column(String(16), default="auto")
    usage_pattern: Mapped[str] = mapped_column(String(500), default="")
    custom_instructions: Mapped[str] = mapped_column(Text, default="")
    preferences_json: Mapped[str] = mapped_column(Text, default="{}")
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)


class KnowledgeFingerprint(Base):
    """Database-enforced idempotency key for imported knowledge records."""
    __tablename__ = "knowledge_fingerprints"
    fingerprint: Mapped[str] = mapped_column(String(64), primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class BenchmarkRun(Base):
    """Admin-only historical record of a local model benchmark."""
    __tablename__ = "benchmark_runs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    model: Mapped[str] = mapped_column(String(200), index=True)
    result_json: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, index=True)


class Migration(Base):
    __tablename__ = "schema_migrations"
    name: Mapped[str] = mapped_column(String(120), primary_key=True)
    completed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class Database:
    """Small SQLAlchemy unit-of-work wrapper; safe for SQLite web workers."""

    def __init__(self, url: str | None = None):
        configured_url = (url or os.getenv("TAMANNA_DATABASE_URL") or "").strip()
        self.url = configured_url or (
            "sqlite:///" + (DATA_DIR / "tamanna.sqlite3").as_posix()
        )
        options = {"future": True, "pool_pre_ping": True}
        if self.url.startswith("sqlite"):
            options["connect_args"] = {"check_same_thread": False, "timeout": 15}
        self.engine = create_engine(self.url, **options)
        if self.url.startswith("sqlite"):
            @event.listens_for(self.engine, "connect")
            def _enable_foreign_keys(connection, _record):
                cursor = connection.cursor()
                cursor.execute("PRAGMA foreign_keys=ON")
                cursor.close()
        self.Session = sessionmaker(bind=self.engine, autoflush=False, expire_on_commit=False)

    def init(self) -> None:
        Base.metadata.create_all(self.engine)
        # create_all() does not add indexes to tables that already exist.
        # Create this additive index explicitly so upgraded databases benefit too.
        memory_index = next(
            index
            for index in Memory.__table__.indexes
            if index.name == "ix_memories_user_id_id"
        )
        memory_index.create(self.engine, checkfirst=True)

    def backup_to(self, destination: str | Path) -> Path:
        """Create a consistent SQLite backup without modifying the live database."""
        if not self.url.startswith("sqlite"):
            raise ValueError("Database backup is currently supported for SQLite only")
        source_name = self.engine.url.database
        if not source_name or source_name == ":memory:":
            raise ValueError("A file-backed SQLite database is required for backup")

        source_path = Path(source_name).expanduser().resolve()
        target_path = Path(destination).expanduser().resolve()
        if source_path == target_path:
            raise ValueError("Backup destination must differ from the live database")
        if target_path.exists():
            raise FileExistsError(f"Backup destination already exists: {target_path}")

        self.init()
        target_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            with self.engine.connect() as source:
                with sqlite3.connect(str(target_path)) as target:
                    source.connection.driver_connection.backup(target)
        except Exception:
            target_path.unlink(missing_ok=True)
            raise
        return target_path

    @staticmethod
    def restore_backup_to(backup: str | Path, destination: str | Path) -> Path:
        """Restore a validated SQLite backup into a new, non-existing database file."""
        backup_path = Path(backup).expanduser().resolve()
        target_path = Path(destination).expanduser().resolve()
        if not backup_path.is_file():
            raise FileNotFoundError(f"Backup file not found: {backup_path}")
        if backup_path == target_path:
            raise ValueError("Restore destination must differ from the backup file")
        if target_path.exists():
            raise FileExistsError(f"Restore destination already exists: {target_path}")

        target_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            with sqlite3.connect(f"{backup_path.as_uri()}?mode=ro", uri=True) as source:
                integrity = source.execute("PRAGMA integrity_check").fetchone()
                if not integrity or integrity[0] != "ok":
                    raise ValueError("Backup failed SQLite integrity check")
                tables = {
                    row[0]
                    for row in source.execute(
                        "SELECT name FROM sqlite_master WHERE type='table'"
                    )
                }
                required_tables = {"users", "conversations", "messages", "memories"}
                if not required_tables.issubset(tables):
                    missing = ", ".join(sorted(required_tables - tables))
                    raise ValueError(
                        f"Backup is missing required Tamanna database tables: {missing}"
                    )
                with sqlite3.connect(str(target_path)) as target:
                    source.backup(target)
                    restored_integrity = target.execute(
                        "PRAGMA integrity_check"
                    ).fetchone()
                    if not restored_integrity or restored_integrity[0] != "ok":
                        raise ValueError("Restored database failed integrity check")
        except Exception:
            target_path.unlink(missing_ok=True)
            raise
        return target_path

    def ping(self) -> bool:
        with self.engine.connect() as connection:
            connection.exec_driver_sql("SELECT 1")
        return True

    def ensure_user(self, email: str, name: str = "") -> int:
        if not isinstance(email, str) or "@" not in email:
            raise ValueError("A valid user email is required")
        self.init()
        normalized_email = email.strip().lower()
        with self.Session.begin() as session:
            user = session.scalar(select(User).where(User.email == normalized_email))
            if user is None:
                user = User(email=normalized_email, name=(name or "").strip()[:80] or None)
                session.add(user)
                session.flush()
            elif name and user.name != name.strip()[:80]:
                user.name = name.strip()[:80]
            user_id = user.id
        return user_id

    def update_user_profile(self, *, user_id: int, name: str, email: str) -> bool:
        """Update the profile name/email for the identified account."""
        if user_id is None:
            raise ValueError("user_id is required")
        clean_name = str(name).strip()
        clean_email = str(email).strip().lower()
        if not clean_name or len(clean_name) > 80:
            raise ValueError("name must contain 1 to 80 characters")
        if len(clean_email) > 254 or "@" not in clean_email:
            raise ValueError("A valid email is required")
        self.init()
        with self.Session.begin() as session:
            user = session.get(User, user_id)
            if user is None:
                raise LookupError("User not found")
            existing = session.scalar(select(User).where(
                User.email == clean_email, User.id != user_id
            ))
            if existing is not None:
                raise ValueError("Email is already in use")
            user.name = clean_name
            user.email = clean_email
        return True

    def get_user_settings(self, *, user_id: int) -> dict[str, object]:
        """Return profile customization for this authenticated user only."""
        if user_id is None:
            raise ValueError("user_id is required")
        self.init()
        with self.Session() as session:
            user = session.get(User, user_id)
            if user is None:
                raise LookupError("User not found")
            settings = session.get(UserSettings, user_id)
            return {
                "user_id": user.id,
                "name": user.name or "",
                "email": user.email or "",
                "language": settings.language if settings else "auto",
                "usage_pattern": settings.usage_pattern if settings else "",
                "custom_instructions": settings.custom_instructions if settings else "",
                "preferences": json.loads(settings.preferences_json) if settings else {},
            }

    def update_user_settings(
        self, *, user_id: int, language: str = "auto",
        usage_pattern: str = "", custom_instructions: str = "",
        preferences: dict[str, object] | None = None,
    ) -> bool:
        """Update only the authenticated user's language and customization settings."""
        if user_id is None:
            raise ValueError("user_id is required")
        language = str(language).strip().lower()
        if language not in {"auto", "en", "bn", "hi", "ar"}:
            raise ValueError("language must be auto, en, bn, hi, or ar")
        if len(str(usage_pattern)) > 500 or len(str(custom_instructions)) > 4000:
            raise ValueError("User settings exceed the allowed length")
        if preferences is not None and not isinstance(preferences, dict):
            raise ValueError("preferences must be an object")
        self.init()
        with self.Session.begin() as session:
            if session.get(User, user_id) is None:
                raise LookupError("User not found")
            settings = session.get(UserSettings, user_id)
            if settings is None:
                settings = UserSettings(user_id=user_id)
                session.add(settings)
            settings.language = language
            settings.usage_pattern = str(usage_pattern).strip()
            settings.custom_instructions = str(custom_instructions).strip()
            settings.preferences_json = json.dumps(
                preferences or {}, ensure_ascii=False
            )[:10000]
        return True

    def save_chat_pair(
        self, user_message: str, assistant_reply: str,
        conversation_id: str = "default", user_id: int | None = None,
    ) -> str:
        if not isinstance(user_message, str) or not isinstance(assistant_reply, str):
            raise TypeError("Chat messages must be strings")
        conversation_id = (conversation_id or "default")[:64]
        with self.Session.begin() as session:
            conversation = session.get(Conversation, conversation_id)
            if conversation is None:
                title = user_message[:197] + "..." if len(user_message) > 200 else user_message or "New conversation"
                conversation = Conversation(id=conversation_id, user_id=user_id, title=title)
                session.add(conversation)
            elif conversation.user_id != user_id:
                raise PermissionError("Conversation does not belong to this user")
            conversation.updated_at = utcnow()
            session.add_all([
                Message(conversation_id=conversation_id, role="user", content=user_message),
                Message(conversation_id=conversation_id, role="assistant", content=assistant_reply),
            ])
        return conversation_id

    def list_conversations(self, *, user_id: int, limit: int = 50) -> list[dict[str, object]]:
        """List recent conversations owned by one authenticated user."""
        if user_id is None:
            raise ValueError("user_id is required")
        self.init()
        limit = max(1, min(int(limit), 100))
        with self.Session() as session:
            rows = session.scalars(
                select(Conversation).where(Conversation.user_id == user_id)
                .order_by(Conversation.updated_at.desc()).limit(limit)
            )
            return [
                {"id": item.id, "title": item.title,
                 "created_at": item.created_at.isoformat(),
                 "updated_at": item.updated_at.isoformat()}
                for item in rows
            ]

    def delete_conversation(self, conversation_id: str, *, user_id: int) -> bool:
        """Delete a conversation only when it belongs to the supplied user."""
        if user_id is None:
            raise ValueError("user_id is required")
        self.init()
        with self.Session.begin() as session:
            conversation = session.scalar(select(Conversation).where(
                Conversation.id == conversation_id, Conversation.user_id == user_id
            ))
            if conversation is None:
                return False
            session.delete(conversation)
        return True

    def load_history(
        self, conversation_id: str | None = None, user_id: int | None = None,
        limit_pairs: int | None = None,
    ) -> list[dict[str, str]]:
        """Load recent complete user/assistant pairs, scoped to the owner when supplied."""
        with self.Session() as session:
            statement = select(Message).join(Conversation).order_by(Message.created_at.desc(), Message.id.desc())
            if conversation_id:
                statement = statement.where(Message.conversation_id == conversation_id)
            statement = statement.where(Conversation.user_id == user_id)
            if limit_pairs is not None:
                limit_pairs = max(1, min(int(limit_pairs), 100))
                statement = statement.limit(limit_pairs * 2)
            messages = list(session.scalars(statement))
        messages.reverse()
        history: list[dict[str, str]] = []
        pending_user: Message | None = None
        for message in messages:
            if message.role == "user":
                pending_user = message
            elif message.role == "assistant" and pending_user is not None:
                history.append({
                    "time": message.created_at.isoformat(),
                    "user": pending_user.content,
                    "assistant": message.content,
                })
                pending_user = None
        return history

    def add_memory(
        self, content: str, *, user_id: int | None = None,
        metadata: dict[str, object] | None = None,
    ) -> int:
        if not isinstance(content, str) or not content.strip():
            raise ValueError("Memory content must be non-empty text")
        self.init()
        with self.Session.begin() as session:
            record = Memory(
                user_id=user_id,
                content=content.strip(),
                metadata_json=json.dumps(metadata or {}, ensure_ascii=False),
            )
            session.add(record)
            session.flush()
            memory_id = record.id
        return memory_id

    def list_memory_records(self, *, user_id: int, limit: int = 100) -> list[dict[str, object]]:
        """List memory records and metadata for one authenticated user."""
        if user_id is None:
            raise ValueError("user_id is required")
        self.init()
        limit = max(1, min(int(limit), 500))
        with self.Session() as session:
            statement = select(Memory).where(Memory.user_id == user_id).order_by(
                Memory.created_at.desc(), Memory.id.desc()
            ).limit(limit)
            return [
                {"id": item.id, "content": item.content,
                 "metadata": json.loads(item.metadata_json),
                 "created_at": item.created_at.isoformat()}
                for item in session.scalars(statement)
            ]

    def list_memories(self, *, user_id: int | None = None, limit: int = 100) -> list[str]:
        self.init()
        limit = max(1, min(int(limit), 500))
        with self.Session() as session:
            statement = select(Memory).order_by(Memory.created_at.desc(), Memory.id.desc()).limit(limit)
            statement = statement.where(Memory.user_id == user_id)
            return [item.content for item in session.scalars(statement)]

    def update_memory(self, memory_id: int, content: str, *, user_id: int) -> bool:
        """Update only a memory owned by the authenticated user."""
        if user_id is None:
            raise ValueError("user_id is required for persistent memory updates")
        if not isinstance(content, str) or not content.strip():
            raise ValueError("Memory content must be non-empty text")
        self.init()
        with self.Session.begin() as session:
            record = session.scalar(select(Memory).where(Memory.id == int(memory_id), Memory.user_id == user_id))
            if record is None:
                return False
            record.content = content.strip()[:10000]
        return True

    def delete_memory(self, memory_id: int, *, user_id: int) -> bool:
        """Delete only a memory owned by the authenticated user."""
        if user_id is None:
            raise ValueError("user_id is required for persistent memory deletion")
        self.init()
        with self.Session.begin() as session:
            record = session.scalar(select(Memory).where(Memory.id == int(memory_id), Memory.user_id == user_id))
            if record is None:
                return False
            session.delete(record)
        return True


    def save_benchmark_run(self, *, model: str, result: dict[str, object]) -> int:
        """Persist benchmark metrics without prompts, responses, or user content."""
        clean_model = str(model).strip()[:200]
        if not clean_model or not isinstance(result, dict):
            raise ValueError("A model name and benchmark result are required")
        safe_result = json.dumps(result, ensure_ascii=False, allow_nan=False)
        self.init()
        with self.Session.begin() as session:
            record = BenchmarkRun(model=clean_model, result_json=safe_result)
            session.add(record)
            session.flush()
            return record.id

    def list_benchmark_runs(self, *, limit: int = 20) -> list[dict[str, object]]:
        """Return recent benchmark summaries, newest first."""
        self.init()
        limit = max(1, min(int(limit), 100))
        with self.Session() as session:
            rows = session.scalars(
                select(BenchmarkRun).order_by(
                    BenchmarkRun.created_at.desc(), BenchmarkRun.id.desc()
                ).limit(limit)
            )
            return [
                {
                    "id": row.id,
                    "model": row.model,
                    "created_at": row.created_at.isoformat(),
                    "result": json.loads(row.result_json),
                }
                for row in rows
            ]

    def migrate_legacy_json(self, json_path: str | Path) -> dict[str, object]:
        path = Path(json_path)
        if not path.is_file():
            return {"imported": 0, "backup": None, "status": "not_found"}
        self.init()
        with self.Session() as session:
            if session.get(Migration, "legacy_chat_history_v1"):
                return {"imported": 0, "backup": None, "status": "already_migrated"}
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        backup = path.with_name(path.name + ".bak." + stamp)
        suffix = 1
        while backup.exists():
            backup = path.with_name(path.name + ".bak." + stamp + "." + str(suffix))
            suffix += 1
        shutil.copy2(path, backup)
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise ValueError(f"Legacy history is backed up at {backup}, but could not be parsed") from exc
        if not isinstance(raw, list):
            raise ValueError(f"Legacy history is backed up at {backup}, but must be a JSON array")
        imported = 0
        with self.Session.begin() as session:
            conversation = session.get(Conversation, "legacy-import")
            if conversation is None:
                session.add(Conversation(id="legacy-import", title="Imported chat history"))
            for index, item in enumerate(raw):
                if not isinstance(item, dict):
                    continue
                user_text, assistant_text = item.get("user"), item.get("assistant")
                if isinstance(user_text, str) and isinstance(assistant_text, str):
                    stamp_value = str(item.get("time") or index)
                    session.add_all([
                        Message(conversation_id="legacy-import", role="user", content=user_text,
                                legacy_key=f"legacy:{index}:user:{stamp_value}"),
                        Message(conversation_id="legacy-import", role="assistant", content=assistant_text,
                                legacy_key=f"legacy:{index}:assistant:{stamp_value}"),
                    ])
                    imported += 1
                elif item.get("role") in {"user", "assistant"} and isinstance(item.get("content"), str):
                    session.add(Message(
                        conversation_id="legacy-import", role=item["role"], content=item["content"],
                        legacy_key=f"legacy:{index}:{item['role']}",
                    ))
                    imported += 1
            session.add(Migration(name="legacy_chat_history_v1"))
        return {"imported": imported, "backup": str(backup), "status": "migrated"}


database = Database()


def init_database() -> None:
    database.init()


def migrate_legacy_json(json_path: str | Path) -> dict[str, object]:
    return database.migrate_legacy_json(json_path)


def save_chat(
    user_message: str, assistant_reply: str, conversation_id: str = "default",
    user_id: int | None = None,
) -> str:
    return database.save_chat_pair(user_message, assistant_reply, conversation_id, user_id)


def load_history(
    conversation_id: str | None = None, user_id: int | None = None
) -> list[dict[str, str]]:
    return database.load_history(conversation_id, user_id)


__all__ = [
    "Base", "User", "Conversation", "Message", "Memory", "Migration",
    "KnowledgeFingerprint", "BenchmarkRun", "Database", "database", "init_database", "migrate_legacy_json",
    "save_chat", "load_history",
]
