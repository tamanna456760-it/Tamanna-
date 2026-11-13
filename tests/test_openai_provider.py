"""Regression tests for the server-side OpenAI provider."""
import asyncio

import httpx
import pytest

from tamanna_ai.integrations.openai import OpenAIClient, OpenAIError
from tamanna_ai.integrations.provider import (
    ModelConfigurationError,
    OpenAIProvider,
    get_model_provider,
)


def test_openai_client_requires_server_api_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(ValueError, match="OPENAI_API_KEY is required"):
        OpenAIClient()


def test_openai_provider_selected_from_private_environment(monkeypatch):
    monkeypatch.setenv("TAMANNA_MODEL_PROVIDER", "openai")
    monkeypatch.setenv("OPENAI_API_KEY", "test-key-not-a-real-secret")
    monkeypatch.setenv("TAMANNA_OPENAI_MODEL", "gpt-5.5")
    assert isinstance(get_model_provider(), OpenAIProvider)


def test_openai_provider_rejects_missing_key(monkeypatch):
    monkeypatch.setenv("TAMANNA_MODEL_PROVIDER", "openai")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(ModelConfigurationError, match="OPENAI_API_KEY is required"):
        get_model_provider()


def test_openai_client_posts_to_responses_api_and_extracts_text(monkeypatch):
    captured = {}

    class FakeAsyncClient:
        def __init__(self, **kwargs):
            captured["client_options"] = kwargs

        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            return False

        async def post(self, url, headers, json):
            captured["url"] = url
            captured["headers"] = headers
            captured["payload"] = json
            request = httpx.Request("POST", url)
            return httpx.Response(
                200,
                request=request,
                json={
                    "output": [{
                        "type": "message",
                        "content": [
                            {"type": "output_text", "text": "Hello "},
                            {"type": "output_text", "text": "Tamanna"},
                        ],
                    }]
                },
            )

    monkeypatch.setattr("tamanna_ai.integrations.openai.httpx.AsyncClient", FakeAsyncClient)
    client = OpenAIClient(api_key="test-key", model="gpt-5.5")
    answer = asyncio.run(client.generate("Say hello"))

    assert answer == "Hello Tamanna"
    assert captured["url"] == "https://api.openai.com/v1/responses"
    assert captured["headers"]["Authorization"] == "Bearer test-key"
    assert captured["payload"]["model"] == "gpt-5.5"
    assert captured["payload"]["input"] == "Say hello"
    assert captured["client_options"]["trust_env"] is False
    assert captured["client_options"]["follow_redirects"] is False


def test_openai_client_rejects_empty_output(monkeypatch):
    class FakeAsyncClient:
        def __init__(self, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            return False

        async def post(self, url, headers, json):
            return httpx.Response(
                200, request=httpx.Request("POST", url), json={"output": []}
            )

    monkeypatch.setattr("tamanna_ai.integrations.openai.httpx.AsyncClient", FakeAsyncClient)
    with pytest.raises(OpenAIError, match="no text output"):
        asyncio.run(OpenAIClient(api_key="test-key").generate("test"))


def test_openai_client_does_not_leak_provider_error_body(monkeypatch):
    class FakeAsyncClient:
        def __init__(self, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            return False

        async def post(self, url, headers, json):
            return httpx.Response(
                401,
                request=httpx.Request("POST", url),
                text="sensitive provider diagnostic body",
            )

    monkeypatch.setattr("tamanna_ai.integrations.openai.httpx.AsyncClient", FakeAsyncClient)
    with pytest.raises(OpenAIError) as error:
        asyncio.run(OpenAIClient(api_key="test-key").generate("test"))
    assert "sensitive provider diagnostic body" not in str(error.value)
