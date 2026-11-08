"""Local Ollama-compatible inference client; no hosted model API or API key."""
from __future__ import annotations

import os
from urllib.parse import urlsplit

import httpx


class OllamaError(RuntimeError):
    """Local model runtime, network, or response error."""


class OllamaClient:
    def __init__(
        self,
        base_url: str | None = None,
        model: str | None = None,
        timeout: float = 120.0,
    ):
        self.base_url = (base_url or os.getenv(
            "TAMANNA_OLLAMA_URL", "http://127.0.0.1:11434"
        )).strip().rstrip("/")
        self.model = (model or os.getenv(
            "TAMANNA_OLLAMA_MODEL", "qwen2.5:7b"
        )).strip()
        self.timeout = float(timeout)

        parsed = urlsplit(self.base_url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ValueError("Ollama URL must be an absolute HTTP(S) URL")
        if parsed.username or parsed.password or parsed.query or parsed.fragment:
            raise ValueError("Ollama URL must not contain credentials, query, or fragment")
        if not self.model or len(self.model) > 200:
            raise ValueError("A valid local model name is required")
        if self.timeout <= 0:
            raise ValueError("timeout must be positive")

    async def generate(self, prompt: str, *, temperature: float = 0.2,
                       max_output_tokens: int = 2048) -> str:
        prompt = prompt.strip()
        if not prompt:
            raise ValueError("Prompt cannot be empty")
        if not 0 <= temperature <= 2:
            raise ValueError("temperature must be between 0 and 2")
        if not 1 <= max_output_tokens <= 32768:
            raise ValueError("Invalid max_output_tokens")

        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_output_tokens,
            },
        }
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/chat", json=payload
                )
                response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise OllamaError(
                f"Local model runtime returned HTTP {exc.response.status_code}"
            ) from exc
        except httpx.HTTPError as exc:
            raise OllamaError(
                f"Cannot reach local model runtime ({type(exc).__name__}). "
                "Check that Ollama is installed, running, and the model is available."
            ) from exc

        try:
            data = response.json()
            answer = data["message"]["content"]
        except (ValueError, KeyError, TypeError) as exc:
            raise OllamaError("Local model runtime returned an invalid response.") from exc
        if not isinstance(answer, str) or not answer.strip():
            raise OllamaError("Local model returned an empty response.")
        return answer.strip()


__all__ = ["OllamaClient", "OllamaError"]
