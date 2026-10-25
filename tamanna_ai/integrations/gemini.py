
"""Tamanna AI: asynchronous Gemini API client."""
from __future__ import annotations

import os
import httpx

DEFAULT_MODEL = "gemini-2.5-flash"
API_BASE = "https://generativelanguage.googleapis.com/v1beta/models"


class GeminiError(RuntimeError):
    """Gemini configuration, network, or API error."""


class GeminiClient:
    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
        timeout: float = 30.0,
    ):
        self.api_key = (
            api_key if api_key is not None
            else os.getenv("GEMINI_API_KEY", "")
        ).strip()
        self.model = (
            model or os.getenv("GEMINI_MODEL", DEFAULT_MODEL)
        ).strip()
        self.timeout = float(timeout)

        if not self.model or "/" in self.model or ":" in self.model:
            raise ValueError("Invalid Gemini model identifier")
        if self.timeout <= 0:
            raise ValueError("timeout must be positive")

    async def generate(
        self,
        prompt: str,
        *,
        temperature: float = 0.2,
        max_output_tokens: int = 1024,
    ) -> str:
        if not self.api_key:
            raise GeminiError("GEMINI_API_KEY is not configured.")

        prompt = prompt.strip()
        if not prompt:
            raise ValueError("Prompt cannot be empty")
        if not 0 <= temperature <= 2:
            raise ValueError("temperature must be between 0 and 2")
        if not 1 <= max_output_tokens <= 65536:
            raise ValueError("Invalid max_output_tokens")

        url = f"{API_BASE}/{self.model}:generateContent"
        payload = {
            "contents": [
                {"role": "user", "parts": [{"text": prompt}]}
            ],
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_output_tokens,
            },
        }

        try:
            async with httpx.AsyncClient(
                timeout=self.timeout
            ) as client:
                response = await client.post(
                    url,
                    headers={"x-goog-api-key": self.api_key},
                    json=payload,
                )
        except httpx.HTTPError as exc:
            raise GeminiError(
                f"Gemini network request failed: {type(exc).__name__}"
            ) from exc

        if response.is_error:
            try:
                detail = response.json().get(
                    "error", {}
                ).get("message", "Request rejected")
            except (ValueError, AttributeError):
                detail = "Request rejected"

            raise GeminiError(
                f"Gemini HTTP {response.status_code}: {detail}"
            )

        try:
            data = response.json()
            candidates = data["candidates"]
            parts = candidates[0]["content"]["parts"]
            answer = "\n".join(
                part["text"]
                for part in parts
                if isinstance(part.get("text"), str)
            )
        except (ValueError, KeyError, IndexError, TypeError) as exc:
            raise GeminiError(
                "Gemini returned an unexpected response format."
            ) from exc

        if not answer.strip():
            raise GeminiError("Gemini returned an empty response.")

        return answer.strip()


async def generate_text(prompt: str, **kwargs) -> str:
    """Convenience function using environment configuration."""
    return await GeminiClient().generate(prompt, **kwargs)
