"""Database-backed, administrator-only control-center APIs.

These endpoints intentionally expose no credentials, password hashes, or host paths.
Destructive user/deployment operations are not provided by this module.
"""
import json
import os
import sqlite3
import time
from datetime import datetime, timezone

from fastapi import APIRouter, Cookie, HTTPException, Query, Request
from pydantic import BaseModel, Field

from tamanna_ai.authentication.router import (
    COOKIE, DB as AUTH_DB, check_origin, current_user, rate_limit_user_action,
)

router = APIRouter(prefix="/api/admin", tags=["admin-control-center"])


def _connect():
    connection = sqlite3.connect(str(AUTH_DB), timeout=10)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys=ON")
    return connection


def _init_tables():
    with _connect() as db:
        db.execute("""CREATE TABLE IF NOT EXISTS admin_app_settings (
            setting_key TEXT PRIMARY KEY, setting_value TEXT NOT NULL,
            updated_at TEXT NOT NULL, updated_by INTEGER NOT NULL
        )""")
        db.execute("""CREATE TABLE IF NOT EXISTS admin_audit_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT, actor_user_id INTEGER NOT NULL,
            action TEXT NOT NULL, target TEXT NOT NULL DEFAULT '',
            details_json TEXT NOT NULL DEFAULT '{}', created_at TEXT NOT NULL
        )""")
        db.execute("CREATE INDEX IF NOT EXISTS ix_admin_audit_created ON admin_audit_events(created_at)")


def _admin(token):
    user = current_user(token)
    if not user:
        raise HTTPException(status_code=401, detail="Sign in required.")
    allowed = {
        value.strip().lower()
        for value in os.getenv("TAMANNA_ADMIN_EMAIL", "").split(",")
        if value.strip()
    }
    if not allowed:
        raise HTTPException(status_code=503, detail="Admin access is disabled until TAMANNA_ADMIN_EMAIL is configured.")
    if str(user.get("email") or "").strip().lower() not in allowed:
        raise HTTPException(status_code=403, detail="Administrator access required.")
    _init_tables()
    return user


def _audit(actor_id, action, target="", details=None):
    with _connect() as db:
        db.execute(
            "INSERT INTO admin_audit_events(actor_user_id,action,target,details_json,created_at) VALUES(?,?,?,?,?)",
            (actor_id, action, target[:180], json.dumps(details or {}, ensure_ascii=False)[:4000],
             datetime.now(timezone.utc).isoformat()),
        )


class AppSettingsUpdate(BaseModel):
    values: dict[str, str | int | float | bool | None] = Field(min_length=1, max_length=20)


@router.get("/users")
def admin_users(token: str | None = Cookie(default=None, alias=COOKIE),
                limit: int = Query(default=50, ge=1, le=200), offset: int = Query(default=0, ge=0)):
    _admin(token)
    with _connect() as db:
        total = db.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        rows = db.execute(
            "SELECT id,email,name,created_at FROM users ORDER BY id DESC LIMIT ? OFFSET ?",
            (limit, offset),
        ).fetchall()
    return {"ok": True, "total": total, "limit": limit, "offset": offset,
            "users": [dict(row) for row in rows]}


@router.get("/analytics")
def admin_analytics(token: str | None = Cookie(default=None, alias=COOKIE)):
    _admin(token)
    with _connect() as db:
        users = db.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        sessions = db.execute("SELECT COUNT(*) FROM sessions WHERE expires>?", (int(time.time()),)).fetchone()[0]
        audit_events = db.execute("SELECT COUNT(*) FROM admin_audit_events").fetchone()[0]
    from tamanna_ai.persistence.database import database, Message
    from sqlalchemy import func, select
    with database.Session() as session:
        messages = session.scalar(select(func.count()).select_from(Message)) or 0
    return {"ok": True, "analytics": {
        "registered_users": users, "active_sessions": sessions,
        "chat_messages": messages, "admin_audit_events": audit_events,
        "measured_at": datetime.now(timezone.utc).isoformat(),
    }, "source": "authentication_and_application_databases"}


@router.get("/settings")
def get_admin_settings(token: str | None = Cookie(default=None, alias=COOKIE)):
    _admin(token)
    with _connect() as db:
        rows = db.execute(
            "SELECT setting_key,setting_value,updated_at FROM admin_app_settings ORDER BY setting_key"
        ).fetchall()
    values = {}
    for row in rows:
        try:
            values[row["setting_key"]] = json.loads(row["setting_value"])
        except (TypeError, ValueError):
            values[row["setting_key"]] = None
    return {"ok": True, "settings": values, "updated": [dict(row) for row in rows]}


@router.patch("/settings")
def update_admin_settings(payload: AppSettingsUpdate, request: Request,
                          token: str | None = Cookie(default=None, alias=COOKIE)):
    user = _admin(token)
    check_origin(request)
    rate_limit_user_action(user["id"], "admin_settings_update", limit=10)
    allowed_keys = {"maintenance_mode", "public_signup_enabled", "default_language", "announcement"}
    unknown = set(payload.values) - allowed_keys
    if unknown:
        raise HTTPException(status_code=422, detail={"message": "Unsupported setting keys.", "keys": sorted(unknown)})
    for key, value in payload.values.items():
        if key in {"maintenance_mode", "public_signup_enabled"} and not isinstance(value, bool):
            raise HTTPException(status_code=422, detail=f"{key} must be boolean.")
        if key == "default_language" and value not in {"auto", "bn", "en", "hi", "ar"}:
            raise HTTPException(status_code=422, detail="default_language is not supported.")
        if key == "announcement" and (not isinstance(value, str) or len(value) > 500):
            raise HTTPException(status_code=422, detail="announcement must be text up to 500 characters.")
    now = datetime.now(timezone.utc).isoformat()
    with _connect() as db:
        for key, value in payload.values.items():
            db.execute(
                """INSERT INTO admin_app_settings(setting_key,setting_value,updated_at,updated_by)
                   VALUES(?,?,?,?) ON CONFLICT(setting_key) DO UPDATE SET
                   setting_value=excluded.setting_value,updated_at=excluded.updated_at,
                   updated_by=excluded.updated_by""",
                (key, json.dumps(value, ensure_ascii=False), now, user["id"]),
            )
    _audit(user["id"], "settings.updated", "application", {"keys": sorted(payload.values)})
    return {"ok": True, "updated_keys": sorted(payload.values)}


@router.get("/memory/summary")
def admin_memory_summary(token: str | None = Cookie(default=None, alias=COOKIE)):
    _admin(token)
    from tamanna_ai.persistence.database import database
    with database.Session() as session:
        from tamanna_ai.persistence.database import Memory
        from sqlalchemy import func, select
        count = session.scalar(select(func.count()).select_from(Memory)) or 0
    return {"ok": True, "memory": {"records": count, "source": "application_database"}}


@router.get("/audit-logs")
def admin_audit_logs(token: str | None = Cookie(default=None, alias=COOKIE),
                     limit: int = Query(default=50, ge=1, le=200), offset: int = Query(default=0, ge=0)):
    _admin(token)
    with _connect() as db:
        total = db.execute("SELECT COUNT(*) FROM admin_audit_events").fetchone()[0]
        rows = db.execute(
            """SELECT id,actor_user_id,action,target,details_json,created_at
               FROM admin_audit_events ORDER BY id DESC LIMIT ? OFFSET ?""", (limit, offset)
        ).fetchall()
    events = []
    for row in rows:
        item = dict(row)
        try:
            item["details"] = json.loads(item.pop("details_json"))
        except (TypeError, ValueError):
            item["details"] = {}
            item.pop("details_json", None)
        events.append(item)
    return {"ok": True, "total": total, "events": events}


@router.get("/sessions")
def admin_sessions(token: str | None = Cookie(default=None, alias=COOKIE),
                   limit: int = Query(default=100, ge=1, le=200)):
    _admin(token)
    with _connect() as db:
        rows = db.execute(
            """SELECT s.user_id,u.email,u.name,s.expires,s.created_at
               FROM sessions s JOIN users u ON u.id=s.user_id
               WHERE s.expires>? ORDER BY s.created_at DESC LIMIT ?""",
            (int(time.time()), limit),
        ).fetchall()
    return {"ok": True, "sessions": [dict(row) for row in rows]}


@router.delete("/sessions/{user_id}")
def revoke_user_sessions(user_id: int, request: Request,
                         token: str | None = Cookie(default=None, alias=COOKIE)):
    actor = _admin(token)
    check_origin(request)
    if user_id == actor["id"]:
        raise HTTPException(status_code=409, detail="Use the normal logout flow to end your own session.")
    rate_limit_user_action(actor["id"], "admin_session_revoke", limit=10)
    with _connect() as db:
        result = db.execute("DELETE FROM sessions WHERE user_id=?", (user_id,))
        revoked = result.rowcount
    _audit(actor["id"], "sessions.revoked", str(user_id), {"revoked_count": revoked})
    return {"ok": True, "user_id": user_id, "revoked_sessions": revoked}


@router.get("/deployment")
def admin_deployment_status(token: str | None = Cookie(default=None, alias=COOKIE)):
    _admin(token)
    return {"ok": True, "deployment": {
        "environment": os.getenv("TAMANNA_ENV", "development"),
        "version": os.getenv("TAMANNA_RELEASE", "unknown"),
        "status": "api_process_running",
        "deployment_actions": "not_supported_by_this_endpoint",
    }}
