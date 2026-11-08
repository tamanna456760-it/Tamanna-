import unittest
from unittest.mock import patch

import httpx

from tamanna_ai.integrations.ollama import OllamaClient, OllamaError


class FakeAsyncClient:
    response = None
    posted = None
    responses = []

    def __init__(self, timeout=None):
        self.timeout = timeout

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        return False

    async def post(self, url, json):
        type(self).posted = (url, json)
        if type(self).responses:
            return type(self).responses.pop(0)
        return type(self).response

    async def get(self, url):
        type(self).requested_url = url
        return type(self).response


class OllamaClientTests(unittest.IsolatedAsyncioTestCase):
    async def test_sends_chat_to_local_runtime_without_api_key(self):
        FakeAsyncClient.response = httpx.Response(
            200, json={"message": {"content": "Local model answer"}},
            request=httpx.Request("POST", "http://127.0.0.1:11434/api/chat")
        )
        client = OllamaClient(
            base_url="http://127.0.0.1:11434",
            model="qwen2.5:7b",
        )
        with patch("tamanna_ai.integrations.ollama.httpx.AsyncClient", FakeAsyncClient):
            answer = await client.generate("Hello")
        self.assertEqual(answer, "Local model answer")
        url, payload = FakeAsyncClient.posted
        self.assertEqual(url, "http://127.0.0.1:11434/api/chat")
        self.assertEqual(payload["model"], "qwen2.5:7b")
        self.assertFalse(payload["stream"])
        self.assertEqual(payload["messages"][0]["content"], "Hello")


    async def test_lists_loaded_model_resource_footprints(self):
        FakeAsyncClient.response = httpx.Response(
            200, json={"models": [{
                "name": "qwen2.5:7b", "size": 4200000000,
                "size_vram": 3900000000, "context_length": 8192,
                "expires_at": "2026-11-08T15:00:00Z",
            }]},
            request=httpx.Request("GET", "http://127.0.0.1:11434/api/ps"),
        )
        client = OllamaClient(base_url="http://127.0.0.1:11434", model="qwen2.5:7b")
        with patch("tamanna_ai.integrations.ollama.httpx.AsyncClient", FakeAsyncClient):
            models = await client.list_running_models()
        self.assertEqual(FakeAsyncClient.requested_url, "http://127.0.0.1:11434/api/ps")
        self.assertEqual(models[0]["name"], "qwen2.5:7b")
        self.assertEqual(models[0]["memory_bytes"], 3900000000)
        self.assertEqual(models[0]["context_length"], 8192)

    async def test_lists_installed_local_models(self):
        FakeAsyncClient.response = httpx.Response(
            200, json={"models": [{"name": "qwen2.5:7b"}, {"name": "llama3.2:3b"}]},
            request=httpx.Request("GET", "http://127.0.0.1:11434/api/tags")
        )
        client = OllamaClient(base_url="http://127.0.0.1:11434")
        with patch("tamanna_ai.integrations.ollama.httpx.AsyncClient", FakeAsyncClient):
            models = await client.list_models()
        self.assertEqual(models, ["llama3.2:3b", "qwen2.5:7b"])
        self.assertEqual(FakeAsyncClient.requested_url, "http://127.0.0.1:11434/api/tags")


    async def test_benchmark_runs_english_bengali_and_json_checks(self):
        def response(content):
            return httpx.Response(
                200,
                json={
                    "message": {"content": content},
                    "prompt_eval_count": 10,
                    "eval_count": 5,
                    "prompt_eval_duration": 100000000,
                    "eval_duration": 200000000,
                    "total_duration": 300000000,
                    "load_duration": 10000000,
                },
                request=httpx.Request("POST", "http://127.0.0.1:11434/api/chat"),
            )

        FakeAsyncClient.responses = [
            response("42"),
            response("৪২"),
            response('{"ok": true, "count": 3}'),
        ]
        client = OllamaClient(
            base_url="http://127.0.0.1:11434",
            model="qwen2.5:7b",
        )
        with patch("tamanna_ai.integrations.ollama.httpx.AsyncClient", FakeAsyncClient):
            result = await client.benchmark()

        self.assertEqual(result["passed_checks"], 3)
        self.assertEqual(result["total_checks"], 3)
        self.assertEqual(result["instruction_following_percent"], 100.0)
        self.assertEqual(
            [item["id"] for item in result["checks"]],
            ["english_arithmetic", "bengali_arithmetic", "json_format"],
        )
        self.assertEqual(result["output_tokens"], 15)
        self.assertIn("not a general accuracy", result["accuracy_note"])
        self.assertEqual(FakeAsyncClient.responses, [])

    async def test_benchmark_json_check_rejects_wrong_shape_and_boolean_count(self):
        self.assertFalse(OllamaClient._valid_benchmark_json('{"ok": true, "count": 4}'))
        self.assertFalse(OllamaClient._valid_benchmark_json('{"ok": true, "count": true}'))
        self.assertFalse(OllamaClient._valid_benchmark_json('not json'))

    async def test_rejects_empty_prompt(self):
        with self.assertRaises(ValueError):
            await OllamaClient().generate(" ")

    async def test_rejects_invalid_url(self):
        with self.assertRaises(ValueError):
            OllamaClient(base_url="file:///etc/passwd")

    async def test_reports_invalid_response(self):
        FakeAsyncClient.response = httpx.Response(
            200, json={"unexpected": True},
            request=httpx.Request("POST", "http://127.0.0.1:11434/api/chat"),
        )
        with patch("tamanna_ai.integrations.ollama.httpx.AsyncClient", FakeAsyncClient):
            with self.assertRaises(OllamaError):
                await OllamaClient().generate("Hello")


if __name__ == "__main__":
    unittest.main()


class ProviderSelectionTests(unittest.TestCase):
    def test_local_ollama_is_the_default_and_needs_no_api_key(self):
        import os
        from unittest.mock import patch
        from tamanna_ai.integrations.provider import OllamaProvider, get_model_provider

        with patch.dict(os.environ, {
            "TAMANNA_MODEL_PROVIDER": "",
            "TAMANNA_OLLAMA_URL": "http://127.0.0.1:11434",
            "TAMANNA_OLLAMA_MODEL": "qwen2.5:7b",
        }, clear=False):
            os.environ.pop("TAMANNA_MODEL_PROVIDER", None)
            os.environ.pop("GEMINI_API_KEY", None)
            os.environ.pop("TAMANNA_MODEL_API_KEY", None)
            provider = get_model_provider()
        self.assertIsInstance(provider, OllamaProvider)
        self.assertEqual(provider.name, "ollama")

    def test_mock_provider_is_test_only(self):
        import os
        from unittest.mock import patch
        from tamanna_ai.integrations.provider import ModelConfigurationError, get_model_provider

        with patch.dict(os.environ, {
            "TAMANNA_MODEL_PROVIDER": "mock",
            "TAMANNA_ENV": "production",
        }):
            with self.assertRaises(ModelConfigurationError):
                get_model_provider()
