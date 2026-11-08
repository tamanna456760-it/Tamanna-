import unittest
from unittest.mock import patch

import httpx

from tamanna_ai.integrations.ollama import OllamaClient, OllamaError


class FakeAsyncClient:
    response = None
    posted = None

    def __init__(self, timeout=None):
        self.timeout = timeout

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        return False

    async def post(self, url, json):
        type(self).posted = (url, json)
        return type(self).response


class OllamaClientTests(unittest.IsolatedAsyncioTestCase):
    async def test_sends_chat_to_local_runtime_without_api_key(self):
        FakeAsyncClient.response = httpx.Response(
            200, json={"message": {"content": "Local model answer"}}
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

    async def test_rejects_empty_prompt(self):
        with self.assertRaises(ValueError):
            await OllamaClient().generate(" ")

    async def test_rejects_invalid_url(self):
        with self.assertRaises(ValueError):
            OllamaClient(base_url="file:///etc/passwd")

    async def test_reports_invalid_response(self):
        FakeAsyncClient.response = httpx.Response(200, json={"unexpected": True})
        with patch("tamanna_ai.integrations.ollama.httpx.AsyncClient", FakeAsyncClient):
            with self.assertRaises(OllamaError):
                await OllamaClient().generate("Hello")


if __name__ == "__main__":
    unittest.main()
