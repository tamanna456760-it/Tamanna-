"""Regression tests: legacy Gemini integration must remain offline and disabled."""

import asyncio

import pytest

from tamanna_ai.integrations.gemini import GeminiClient, GeminiError


def test_gemini_client_fails_closed_without_reading_api_keys(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "must-not-be-read")
    monkeypatch.setenv("TAMANNA_MODEL_API_KEY", "must-not-be-read")
    client = GeminiClient()
    with pytest.raises(GeminiError, match="Hosted Gemini inference is disabled"):
        asyncio.run(client.generate("Hello"))


def test_gemini_multimodal_client_fails_closed(tmp_path):
    sample = tmp_path / "sample.png"
    sample.write_bytes(b"not-used")
    client = GeminiClient(api_key="ignored-test-key")
    with pytest.raises(GeminiError, match="Hosted Gemini multimodal inference is disabled"):
        asyncio.run(client.generate_with_files("Describe this", [sample]))


def test_empty_or_invalid_arguments_never_trigger_network_calls(monkeypatch):
    import httpx

    def forbidden_client(*args, **kwargs):
        raise AssertionError("The disabled Gemini compatibility shim must never create an HTTP client.")

    monkeypatch.setattr(httpx, "AsyncClient", forbidden_client)
    client = GeminiClient(api_key="ignored-test-key")
    with pytest.raises(GeminiError, match="disabled"):
        asyncio.run(client.generate("   "))
