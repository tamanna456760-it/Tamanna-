"""Single model-provider interface for Tamanna AI."""
from __future__ import annotations
import os
from typing import Protocol
from .gemini import GeminiClient, GeminiError

class ModelConfigurationError(RuntimeError):
    """The configured model provider cannot be initialized."""

class ModelProviderError(RuntimeError):
    """A configured model provider failed to generate a response."""

class ModelProvider(Protocol):
    async def generate(self, prompt: str) -> str: ...

class GeminiProvider:
    name = "gemini"

    def __init__(self, api_key: str, model: str | None = None):
        self.client = GeminiClient(api_key=api_key, model=model)

    async def generate(self, prompt: str) -> str:
        try:
            return await self.client.generate(prompt)
        except GeminiError as exc:
            raise ModelProviderError(str(exc)) from exc

    async def generate_with_files(self, prompt: str, file_paths: list[str]) -> str:
        try:
            return await self.client.generate_with_files(prompt, file_paths)
        except GeminiError as exc:
            raise ModelProviderError(str(exc)) from exc

class MockProvider:
    """Deterministic provider allowed only in an explicit test environment."""
    name = "mock"
    async def generate(self, prompt: str) -> str:
        return f"Mock response: {prompt.strip()}"

def get_model_provider() -> ModelProvider:
    provider = os.getenv("TAMANNA_MODEL_PROVIDER", "gemini").strip().lower()
    if provider == "mock":
        if os.getenv("TAMANNA_ENV", "").strip().lower() != "test":
            raise ModelConfigurationError("The mock model provider is available only when TAMANNA_ENV=test.")
        return MockProvider()
    if provider != "gemini":
        raise ModelConfigurationError(f"Unsupported model provider: {provider}")
    api_key = os.getenv("TAMANNA_MODEL_API_KEY", "").strip() or os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        raise ModelConfigurationError(
            "AI model is not configured. Set GEMINI_API_KEY (or TAMANNA_MODEL_API_KEY) in the private .env file."
        )
    return GeminiProvider(api_key=api_key, model=os.getenv("GEMINI_MODEL") or None)

__all__ = [
    "ModelConfigurationError", "ModelProviderError", "ModelProvider",
    "GeminiProvider", "MockProvider", "get_model_provider",
]
