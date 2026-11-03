"""SQLAlchemy persistence for users, conversations, messages, and memories."""
from __future__ import annotations

import json
import os
import shutil
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, create_engine, event, select
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
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    conversation_id: Mapped[str | None] = mapped_column(
        ForeignKey("conversations.id", ondelete="SET NULL"), nullable=True
    )
    content: Mapped[str] = mapped_column(Text)
    metadata_json: Mapped[str] = mapped_column(Text, default="{}")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class Migration(Base):
    __tablename__ = "schema_migrations"
    name: Mapped[str] = mapped_column(String(120), primary_key=True)
    completed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class Database:
    """Small SQLAlchemy unit-of-work wrapper; safe for SQLite web workers."""

    def __init__(self, url: str | None = None):
        self.url = url or os.getenv(
            "TAMANNA_DATABASE_URL",
            "sqlite:///" + (DATA_DIR / "tamanna.sqlite3").as_posix(),
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

    def ping(self) -> bool:
        with self.engine.connect() as connection:
            connection.exec_driver_sql("SELECT 1")
        return True

    def save_chat_pair(self, user_message: str, assistant_reply: str, conversation_id: str = "default") -> str:
        if not isinstance(user_message, str) or not isinstance(assistant_reply, str):
            raise TypeError("Chat messages must be strings")
        conversation_id = (conversation_id or "default")[:64]
        with self.Session.begin() as session:
            conversation = session.get(Conversation, conversation_id)
            if conversation is None:
                title = user_message[:197] + "..." if len(user_message) > 200 else user_message or "New conversation"
                conversation = Conversation(id=conversation_id, title=title)
                session.add(conversation)
            conversation.updated_at = utcnow()
            session.add_all([
                Message(conversation_id=conversation_id, role="user", content=user_message),
                Message(conversation_id=conversation_id, role="assistant", content=assistant_reply),
            ])
        return conversation_id

    def load_history(self, conversation_id: str | None = None) -> list[dict[str, str]]:
        with self.Session() as session:
            statement = select(Message).order_by(Message.created_at, Message.id)
            if conversation_id:
                statement = statement.where(Message.conversation_id == conversation_id)
            messages = list(session.scalars(statement))
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


def save_chat(user_message: str, assistant_reply: str, conversation_id: str = "default") -> str:
    return database.save_chat_pair(user_message, assistant_reply, conversation_id)


def load_history(conversation_id: str | None = None) -> list[dict[str, str]]:
    return database.load_history(conversation_id)


__all__ = [
    "Base", "User", "Conversation", "Message", "Memory", "Migration",
    "Database", "database", "init_database", "migrate_legacy_json",
    "save_chat", "load_history",
]
