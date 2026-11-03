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


def test_chat_api_uses_mock_and_preserves_reply_shape(monkeypatch):
    monkeypatch.setenv("TAMANNA_ENV", "test")
    monkeypatch.setenv("TAMANNA_MODEL_PROVIDER", "mock")
    from Main import app
    response = TestClient(app).post("/api/chat", json={"message": "hello"})
    assert response.status_code == 200
    assert response.json() == {"reply": "Mock response: hello"}


def test_chat_api_returns_503_without_model_key(monkeypatch):
    monkeypatch.setenv("TAMANNA_MODEL_PROVIDER", "gemini")
    monkeypatch.delenv("TAMANNA_MODEL_API_KEY", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    from Main import app
    response = TestClient(app).post("/api/chat", json={"message": "hello"})
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
