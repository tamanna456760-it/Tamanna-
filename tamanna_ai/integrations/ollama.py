"""Local Ollama-compatible inference client; no hosted model API or API key."""
from __future__ import annotations

import json
import os
import re
from typing import AsyncIterator
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

    async def list_models(self) -> list[str]:
        """Return installed local model names from the Ollama runtime."""
        try:
            async with httpx.AsyncClient(timeout=min(self.timeout, 15.0)) as client:
                response = await client.get(f"{self.base_url}/api/tags")
                response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise OllamaError(
                f"Local model runtime returned HTTP {exc.response.status_code}"
            ) from exc
        except httpx.HTTPError as exc:
            raise OllamaError(
                f"Cannot reach local model runtime ({type(exc).__name__})."
            ) from exc

        try:
            models = response.json()["models"]
            names = [
                item["name"] for item in models
                if isinstance(item, dict) and isinstance(item.get("name"), str)
            ]
        except (ValueError, KeyError, TypeError) as exc:
            raise OllamaError("Local model runtime returned an invalid model list.") from exc
        return sorted(set(names))

    async def list_running_models(self) -> list[dict]:
        """Return loaded model names and runtime memory footprints from Ollama."""
        try:
            async with httpx.AsyncClient(timeout=min(self.timeout, 15.0)) as client:
                response = await client.get(f"{self.base_url}/api/ps")
                response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise OllamaError(f"Local model runtime returned HTTP {exc.response.status_code}") from exc
        except httpx.HTTPError as exc:
            raise OllamaError(f"Cannot read loaded model resources ({type(exc).__name__}).") from exc
        try:
            raw_models = response.json()["models"]
            if not isinstance(raw_models, list):
                raise TypeError("models must be a list")
            models = []
            for item in raw_models:
                if not isinstance(item, dict) or not isinstance(item.get("name"), str):
                    continue
                models.append({
                    "name": item["name"][:200],
                    "size_bytes": item.get("size") if isinstance(item.get("size"), int) and item.get("size") >= 0 else None,
                    "memory_bytes": item.get("size_vram") if isinstance(item.get("size_vram"), int) and item.get("size_vram") >= 0 else None,
                    "expires_at": item.get("expires_at") if isinstance(item.get("expires_at"), str) else None,
                    "context_length": item.get("context_length") if isinstance(item.get("context_length"), int) and item.get("context_length") > 0 else None,
                })
            return models
        except (ValueError, KeyError, TypeError) as exc:
            raise OllamaError("Local model runtime returned invalid loaded-model data.") from exc

    async def pull_model(self, model: str) -> AsyncIterator[dict]:
        """Stream Ollama model-pull progress as validated NDJSON events."""
        model = model.strip() if isinstance(model, str) else ""
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._:/-]{0,199}", model):
            raise ValueError("Invalid local model name")
        completed = False
        try:
            async with httpx.AsyncClient(timeout=None) as client:
                async with client.stream(
                    "POST",
                    f"{self.base_url}/api/pull",
                    json={"name": model, "stream": True},
                    timeout=None,
                ) as response:
                    response.raise_for_status()
                    async for line in response.aiter_lines():
                        if not line:
                            continue
                        try:
                            event = json.loads(line)
                        except (ValueError, TypeError) as exc:
                            raise OllamaError("Ollama returned invalid pull progress data.") from exc
                        if not isinstance(event, dict):
                            raise OllamaError("Ollama returned an invalid pull event.")
                        if event.get("error"):
                            raise OllamaError(str(event["error"])[:300])
                        if event.get("done") is True or event.get("status") == "success":
                            completed = True
                        yield event
            if not completed:
                raise OllamaError("Ollama ended the model download without confirming success.")
        except httpx.HTTPStatusError as exc:
            raise OllamaError(
                f"Local model runtime returned HTTP {exc.response.status_code} while downloading."
            ) from exc
        except httpx.HTTPError as exc:
            raise OllamaError(
                f"Model download connection failed ({type(exc).__name__})."
            ) from exc

    async def benchmark(self) -> dict:
        """Run bounded English, Bengali and JSON instruction checks on the local model."""
        import time

        tasks = [
            {
                "id": "english_arithmetic",
                "prompt": "What is 17 + 25? Reply with only the number.",
                "check": lambda answer: bool(re.search(r"(?<!\d)42(?!\d)", answer)),
            },
            {
                "id": "bengali_arithmetic",
                "prompt": "১৭ + ২৫ কত? শুধু উত্তরটি লিখুন।",
                "check": lambda answer: bool(re.search(r"(?<!\d)৪২(?!\d)|(?<!\d)42(?!\d)", answer)),
            },
            {
                "id": "json_format",
                "prompt": 'Return only valid JSON with exactly these keys: "ok" (boolean true) and "count" (number 3).',
                "check": lambda answer: self._valid_benchmark_json(answer),
            },
        ]
        checks = []
        total_wall_ms = 0.0
        prompt_tokens = output_tokens = 0
        prompt_duration = output_duration = total_duration = load_duration = 0

        for task in tasks:
            payload = {
                "model": self.model,
                "messages": [{"role": "user", "content": task["prompt"]}],
                "stream": False,
                "format": "json" if task["id"] == "json_format" else None,
                "options": {"temperature": 0, "num_predict": 48},
            }
            if payload["format"] is None:
                payload.pop("format")
            started = time.perf_counter()
            try:
                async with httpx.AsyncClient(timeout=min(self.timeout, 60.0)) as client:
                    response = await client.post(f"{self.base_url}/api/chat", json=payload)
                    response.raise_for_status()
            except httpx.HTTPStatusError as exc:
                raise OllamaError(
                    f"Local model runtime returned HTTP {exc.response.status_code} during benchmark."
                ) from exc
            except httpx.HTTPError as exc:
                raise OllamaError(
                    f"Local model benchmark connection failed ({type(exc).__name__})."
                ) from exc
            total_wall_ms += (time.perf_counter() - started) * 1000
            try:
                data = response.json()
                answer = data["message"]["content"]
                p_count = int(data.get("prompt_eval_count", 0))
                o_count = int(data.get("eval_count", 0))
                p_duration = int(data.get("prompt_eval_duration", 0))
                o_duration = int(data.get("eval_duration", 0))
                total_duration += int(data.get("total_duration", 0))
                load_duration += int(data.get("load_duration", 0))
            except (ValueError, KeyError, TypeError, OverflowError) as exc:
                raise OllamaError("Ollama returned invalid benchmark metrics.") from exc
            if not isinstance(answer, str) or not answer.strip():
                raise OllamaError("Model returned an empty benchmark response.")
            prompt_tokens += p_count
            output_tokens += o_count
            prompt_duration += p_duration
            output_duration += o_duration
            checks.append({"id": task["id"], "passed": bool(task["check"](answer.strip()))})

        passed = sum(1 for check in checks if check["passed"])
        return {
            "model": self.model,
            "wall_time_ms": round(total_wall_ms, 1),
            "prompt_tokens": prompt_tokens,
            "output_tokens": output_tokens,
            "prompt_tokens_per_second": round(
                prompt_tokens / (prompt_duration / 1_000_000_000), 2
            ) if prompt_duration > 0 else None,
            "generation_tokens_per_second": round(
                output_tokens / (output_duration / 1_000_000_000), 2
            ) if output_duration > 0 else None,
            "total_duration_ms": round(total_duration / 1_000_000, 1)
            if total_duration > 0 else None,
            "model_load_ms": round(load_duration / 1_000_000, 1)
            if load_duration > 0 else None,
            "checks": checks,
            "passed_checks": passed,
            "total_checks": len(checks),
            "instruction_following_percent": round(passed / len(checks) * 100, 1),
            "accuracy_note": "Three basic deterministic instruction checks only; not a general accuracy or GPT/Gemini equivalence score.",
        }

    @staticmethod
    def _valid_benchmark_json(answer: str) -> bool:
        try:
            value = json.loads(answer)
        except (ValueError, TypeError):
            return False
        return (
            isinstance(value, dict)
            and set(value) == {"ok", "count"}
            and value.get("ok") is True
            and value.get("count") == 3
            and not isinstance(value.get("count"), bool)
        )

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
