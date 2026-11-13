"""OpenAI Responses API provider for server-side Tamanna AI inference."""
from __future__ import annotations

import os

import httpx


class OpenAIError(RuntimeError):
    """OpenAI request, transport, or response error."""


class OpenAIClient:
    """Small async HTTP client; reads credentials only from server environment."""

    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
        base_url: str | None = None,
        timeout: float = 60.0,
    ):
        self.api_key = (api_key or os.getenv("OPENAI_API_KEY", "")).strip()
        self.model = (model or os.getenv("TAMANNA_OPENAI_MODEL", "gpt-5.5")).strip()
        self.base_url = (base_url or os.getenv(
            "TAMANNA_OPENAI_BASE_URL", "https://api.openai.com/v1"
        )).strip().rstrip("/")
        self.timeout = float(timeout)

        if not self.api_key:
            raise ValueError("OPENAI_API_KEY is required for the OpenAI provider")
        if len(self.api_key) > 512 or any(ch.isspace() for ch in self.api_key):
            raise ValueError("OPENAI_API_KEY has an invalid format")
        if not self.model or len(self.model) > 100:
            raise ValueError("A valid TAMANNA_OPENAI_MODEL is required")
        if not self.base_url.startswith("https://"):
            raise ValueError("OpenAI API base URL must use HTTPS")
        if self.timeout <= 0:
            raise ValueError("timeout must be positive")

    async def generate(
        self,
        prompt: str,
        *,
        temperature: float = 0.2,
        max_output_tokens: int = 2048,
    ) -> str:
        prompt = prompt.strip() if isinstance(prompt, str) else ""
        if not prompt:
            raise ValueError("Prompt cannot be empty")
        if not 0 <= temperature <= 2:
            raise ValueError("temperature must be between 0 and 2")
        if not 1 <= max_output_tokens <= 32768:
            raise ValueError("Invalid max_output_tokens")

        payload = {
            "model": self.model,
            "input": prompt,
            "max_output_tokens": max_output_tokens,
            "temperature": temperature,
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        try:
            async with httpx.AsyncClient(
                timeout=self.timeout, trust_env=False, follow_redirects=False
            ) as client:
                response = await client.post(
                    f"{self.base_url}/responses",
                    headers=headers,
                    json=payload,
                )
                response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            # Do not return provider response bodies: they may contain sensitive details.
            raise OpenAIError(
                f"OpenAI API returned HTTP {exc.response.status_code}"
            ) from exc
        except httpx.HTTPError as exc:
            raise OpenAIError(
                f"OpenAI API connection failed ({type(exc).__name__})"
            ) from exc

        try:
            data = response.json()
            output = data.get("output", [])
            parts = []
            for item in output:
                if not isinstance(item, dict) or item.get("type") != "message":
                    continue
                for part in item.get("content", []):
                    if (
                        isinstance(part, dict)
                        and part.get("type") == "output_text"
                        and isinstance(part.get("text"), str)
                    ):
                        parts.append(part["text"])
            answer = "".join(parts).strip()
        except (ValueError, AttributeError, TypeError) as exc:
            raise OpenAIError("OpenAI API returned an invalid response") from exc

        if not answer:
            raise OpenAIError("OpenAI API returned no text output")
        return answer


__all__ = ["OpenAIClient", "OpenAIError"]
