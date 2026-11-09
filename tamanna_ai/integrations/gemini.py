"""Deprecated compatibility shim: hosted Gemini inference is disabled.

Tamanna AI's supported model path is private local Ollama. This module remains
only so older imports fail closed with a clear error instead of making a
network request or reading a hosted-model API key.
"""

from __future__ import annotations

from pathlib import Path


class GeminiError(RuntimeError):
    """Raised when an obsolete hosted Gemini integration is invoked."""


class GeminiClient:
    def __init__(self, *args, **kwargs):
        # Deliberately do not read GEMINI_API_KEY or TAMANNA_MODEL_API_KEY.
        self.model = "disabled"

    async def generate(self, prompt: str, **kwargs) -> str:
        raise GeminiError(
            "Hosted Gemini inference is disabled. Configure the private local Ollama provider."
        )

    async def generate_with_files(
        self,
        prompt: str,
        file_paths: list[str | Path],
        **kwargs,
    ) -> str:
        raise GeminiError(
            "Hosted Gemini multimodal inference is disabled. Use a supported local workflow."
        )
