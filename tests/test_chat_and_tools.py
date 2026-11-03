"""Integration tests for model selection, chat API, and safe tools."""
import asyncio
import json
from fastapi.testclient import TestClient
import pytest
from tamanna_ai.integrations.provider import ModelConfigurationError, get_model_provider
from tamanna_ai.tools import safe_tools


def test_gemini_is_default_and_requires_key(monkeypatch):
    monkeypatch.delenv("TAMANNA_MODEL_API_KEY", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("TAMANNA_MODEL_PROVIDER", raising=False)
    with pytest.raises(ModelConfigurationError, match="not configured"):
        get_model_provider()


def test_mock_provider_is_restricted_to_test_environment(monkeypatch):
    monkeypatch.setenv("TAMANNA_MODEL_PROVIDER", "mock")
    monkeypatch.delenv("TAMANNA_ENV", raising=False)
    with pytest.raises(ModelConfigurationError, match="only when TAMANNA_ENV=test"):
        get_model_provider()
    monkeypatch.setenv("TAMANNA_ENV", "test")
    assert asyncio.run(get_model_provider().generate("hello")) == "Mock response: hello"


def _create_chat_test_user(client, monkeypatch, tmp_path):
    from tamanna_ai.authentication import router as auth_router
    import secrets
    monkeypatch.setenv("TAMANNA_SESSION_SECRET", "test-session-secret-with-more-than-32-characters")
    monkeypatch.setattr(auth_router, "COOKIE_SECURE", False)
    monkeypatch.setattr(auth_router, "DB", tmp_path / ("auth-" + secrets.token_hex(4) + ".sqlite3"))
    response = client.post("/api/auth/signup", json={
        "email": "chat-" + secrets.token_hex(4) + "@example.test",
        "name": "Chat Test",
        "password": "a-long-test-password-123",
    })
    assert response.status_code == 201, response.text


def test_chat_api_uses_mock_and_preserves_reply_shape(monkeypatch, tmp_path):
    monkeypatch.setenv("TAMANNA_ENV", "test")
    monkeypatch.setenv("TAMANNA_MODEL_PROVIDER", "mock")
    from Main import app
    with TestClient(app) as client:
        _create_chat_test_user(client, monkeypatch, tmp_path)
        response = client.post("/api/chat", json={"message": "hello"})
        assert response.status_code == 200, response.text
        assert response.json() == {
            "reply": "Mock response: hello",
            "handled": True,
            "source": "mock",
        }
        history = client.get("/api/history")
        assert history.status_code == 200
        assert history.json()["history"][-1]["user"] == "hello"


def test_chat_api_returns_503_without_model_key(monkeypatch, tmp_path):
    monkeypatch.setenv("TAMANNA_MODEL_PROVIDER", "gemini")
    monkeypatch.delenv("TAMANNA_MODEL_API_KEY", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    from Main import app
    with TestClient(app) as client:
        _create_chat_test_user(client, monkeypatch, tmp_path)
        response = client.post("/api/chat", json={"message": "hello"})
        assert response.status_code == 503
        assert "not configured" in response.json()["detail"]


def test_read_doc_is_confined_to_docs_and_logs_calls(tmp_path, monkeypatch):
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "guide.md").write_text("# Safe docs", encoding="utf-8")
    monkeypatch.setattr(safe_tools, "DOCS_DIR", docs)
    monkeypatch.setattr(safe_tools, "LOG_PATH", tmp_path / "tool_calls.jsonl")
    result = safe_tools.read_doc("guide.md")
    assert result["content"] == "# Safe docs"
    with pytest.raises(safe_tools.ToolInputError):
        safe_tools.read_doc("../outside.txt")


def test_tool_registry_rejects_unlisted_tools_and_logs(tmp_path, monkeypatch):
    monkeypatch.setattr(safe_tools, "LOG_PATH", tmp_path / "tool_calls.jsonl")
    with pytest.raises(safe_tools.ToolInputError, match="not allow-listed"):
        asyncio.run(safe_tools.execute_tool("shell", {"command": "id"}))
    records = [json.loads(x) for x in (tmp_path / "tool_calls.jsonl").read_text().splitlines()]
    assert records[-1]["tool"] == "shell"
    assert records[-1]["status"] == "error"



def test_allowlisted_read_doc_call_is_logged_as_success(tmp_path, monkeypatch):
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "readme.md").write_text("read-only", encoding="utf-8")
    monkeypatch.setattr(safe_tools, "DOCS_DIR", docs)
    monkeypatch.setattr(safe_tools, "LOG_PATH", tmp_path / "tool_calls.jsonl")
    result = asyncio.run(safe_tools.execute_tool("read_doc", {"path": "readme.md"}))
    assert result["result"]["content"] == "read-only"
    record = json.loads((tmp_path / "tool_calls.jsonl").read_text().splitlines()[0])
    assert record["tool"] == "read_doc"
    assert record["status"] == "success"


def test_web_search_without_provider_is_logged_and_returns_configuration_error(tmp_path, monkeypatch):
    monkeypatch.delenv("TAMANNA_SEARCH_PROVIDER", raising=False)
    monkeypatch.setattr(safe_tools, "LOG_PATH", tmp_path / "tool_calls.jsonl")
    with pytest.raises(safe_tools.ToolConfigurationError):
        asyncio.run(safe_tools.execute_tool("web_search", {"query": "Tamanna AI"}))
    record = json.loads((tmp_path / "tool_calls.jsonl").read_text().splitlines()[0])
    assert record["tool"] == "web_search"
    assert record["status"] == "error"



def test_history_endpoint_requires_authentication():
    from Main import app
    response = TestClient(app).get("/api/history")
    assert response.status_code == 401
