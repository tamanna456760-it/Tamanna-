"""Model-provider selection for Tamanna AI; local inference is the default."""
from __future__ import annotations

import os
from typing import AsyncIterator, Protocol

from .ollama import OllamaClient, OllamaError
from .model_settings import get_selected_model


class ModelConfigurationError(RuntimeError):
    """The configured model provider cannot be initialized."""


class ModelProviderError(RuntimeError):
    """A configured model provider failed to generate a response."""


class ModelProvider(Protocol):
    async def generate(self, prompt: str) -> str: ...


class OllamaProvider:
    """Uses a model running in the user's own Ollama runtime."""
    name = "ollama"

    def __init__(self, base_url: str | None = None, model: str | None = None):
        self.client = OllamaClient(base_url=base_url, model=model)

    async def list_models(self) -> list[str]:
        try:
            return await self.client.list_models()
        except OllamaError as exc:
            raise ModelProviderError(str(exc)) from exc

    async def pull_model(self, model: str) -> AsyncIterator[dict]:
        try:
            async for event in self.client.pull_model(model):
                yield event
        except (OllamaError, ValueError) as exc:
            raise ModelProviderError(str(exc)) from exc

    async def benchmark(self) -> dict:
        try:
            return await self.client.benchmark()
        except OllamaError as exc:
            raise ModelProviderError(str(exc)) from exc

    async def generate(self, prompt: str) -> str:
        try:
            return await self.client.generate(prompt)
        except OllamaError as exc:
            raise ModelProviderError(str(exc)) from exc


class MockProvider:
    """Deterministic provider allowed only in an explicit test environment."""
    name = "mock"

    async def generate(self, prompt: str) -> str:
        return f"Mock response: {prompt.strip()}"


def get_model_provider() -> ModelProvider:
    provider = os.getenv("TAMANNA_MODEL_PROVIDER", "ollama").strip().lower()
    if provider == "mock":
        if os.getenv("TAMANNA_ENV", "").strip().lower() != "test":
            raise ModelConfigurationError(
                "The mock model provider is available only when TAMANNA_ENV=test."
            )
        return MockProvider()
    if provider == "ollama":
        try:
            return OllamaProvider(
                base_url=os.getenv("TAMANNA_OLLAMA_URL") or None,
                model=get_selected_model() or os.getenv("TAMANNA_OLLAMA_MODEL") or None,
            )
        except (TypeError, ValueError) as exc:
            raise ModelConfigurationError(
                f"Invalid local model configuration: {exc}"
            ) from exc
    raise ModelConfigurationError(
        "Unsupported model provider. Use 'ollama' for local inference or 'mock' in tests."
    )


__all__ = [
    "ModelConfigurationError",
    "ModelProviderError",
    "ModelProvider",
    "OllamaProvider",
    "MockProvider",
    "get_model_provider",
]
