"""Offline tests for Tamanna Gemini integration."""

import asyncio
import httpx
import pytest

from tamanna_ai.integrations.gemini import GeminiClient, GeminiError


def test_missing_api_key():
    client = GeminiClient(api_key="")
    with pytest.raises(GeminiError, match="GEMINI_API_KEY"):
        asyncio.run(client.generate("Hello"))


def test_empty_prompt():
    client = GeminiClient(api_key="test-key")
    with pytest.raises(ValueError, match="Prompt cannot be empty"):
        asyncio.run(client.generate("   "))


def test_successful_generation(monkeypatch):
    class FakeResponse:
        is_error = False
        status_code = 200

        def json(self):
            return {
                "candidates": [{
                    "content": {
                        "parts": [{"text": "Hello from Gemini"}]
                    }
                }]
            }

    class FakeAsyncClient:
        def __init__(self, timeout):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            return False

        async def post(self, url, *, headers, json):
            assert headers["x-goog-api-key"] == "test-key"
            return FakeResponse()

    monkeypatch.setattr(httpx, "AsyncClient", FakeAsyncClient)

    client = GeminiClient(api_key="test-key")
    result = asyncio.run(client.generate("Hello"))

    assert result == "Hello from Gemini"


def test_api_error(monkeypatch):
    class FakeResponse:
        is_error = True
        status_code = 401

        def json(self):
            return {"error": {"message": "Invalid API key"}}

    class FakeAsyncClient:
        def __init__(self, timeout):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            return False

        async def post(self, *args, **kwargs):
            return FakeResponse()

    monkeypatch.setattr(httpx, "AsyncClient", FakeAsyncClient)

    client = GeminiClient(api_key="test-key")

    with pytest.raises(GeminiError, match="Gemini HTTP 401"):
        asyncio.run(client.generate("Hello"))
