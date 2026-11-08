import unittest
from unittest.mock import AsyncMock, patch

from fastapi import HTTPException

from tamanna_ai.api.routes import ChatRequest, chat, model_status


class FakeProvider:
    name = "ollama"

    def __init__(self, answer="Local model response"):
        self.generate = AsyncMock(return_value=answer)


class FakeModelManager:
    name = "ollama"
    client = type("ClientInfo", (), {"model": "qwen2.5:7b"})()

    async def list_models(self):
        return ["qwen2.5:7b", "llama3.2:3b"]


class ChatRouteTests(unittest.IsolatedAsyncioTestCase):
    async def test_chat_uses_configured_local_provider(self):
        provider = FakeProvider()
        with patch("tamanna_ai.api.routes.get_model_provider", return_value=provider):
            result = await chat(ChatRequest(prompt="Explain photosynthesis"))
        self.assertEqual(result.response, "Local model response")
        self.assertEqual(result.provider, "ollama")
        provider.generate.assert_awaited_once_with("Explain photosynthesis")

    async def test_model_status_lists_installed_models(self):
        with patch("tamanna_ai.api.routes.get_model_provider", return_value=FakeModelManager()):
            result = await model_status()
        self.assertEqual(result["status"], "ready")
        self.assertEqual(result["selected_model"], "qwen2.5:7b")
        self.assertIn("llama3.2:3b", result["installed_models"])

    async def test_blank_prompt_is_rejected(self):
        with self.assertRaises(HTTPException) as raised:
            await chat(ChatRequest(prompt="   "))
        self.assertEqual(raised.exception.status_code, 422)


if __name__ == "__main__":
    unittest.main()
