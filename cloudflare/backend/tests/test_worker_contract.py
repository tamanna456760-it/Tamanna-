from __future__ import annotations

import ast
import json
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BACKEND = ROOT / "cloudflare" / "backend"


def test_worker_python_syntax():
    source = (BACKEND / "worker.py").read_text(encoding="utf-8")
    ast.parse(source)


def test_worker_uses_cloudflare_python_asgi_and_d1():
    source = (BACKEND / "worker.py").read_text(encoding="utf-8")
    assert "from workers import asgi" in source
    assert "Default = asgi.entrypoint(app)" in source
    assert 'return runtime(request).DB' in source
    assert '@app.post("/api/chat")' in source
    assert '@app.post("/api/auth/login")' in source


def test_wrangler_config_is_valid_and_has_expected_route():
    config = json.loads((BACKEND / "wrangler.jsonc").read_text(encoding="utf-8"))
    assert config["name"] == "tamanna-api"
    assert config["main"] == "worker.py"
    assert "python_workers" in config["compatibility_flags"]
    assert config["d1_databases"][0]["binding"] == "DB"
    assert config["routes"][0]["pattern"] == "www.bd-king-r7.com/api/*"


def test_d1_schema_creates_expected_tables():
    schema = (BACKEND / "schema.sql").read_text(encoding="utf-8")
    connection = sqlite3.connect(":memory:")
    connection.executescript(schema)
    names = {
        row[0]
        for row in connection.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )
    }
    assert {"users", "sessions", "preferences", "messages", "auth_attempts"} <= names
    connection.close()


def test_local_secrets_template_contains_no_real_credentials():
    template = (BACKEND / ".dev.vars.example").read_text(encoding="utf-8")
    assert "GEMINI_API_KEY=" in template
    assert "TAMANNA_SESSION_SECRET=" in template
    assert "AIza" not in template
