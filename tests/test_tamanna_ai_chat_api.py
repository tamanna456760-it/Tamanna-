import unittest
from unittest.mock import AsyncMock, patch

from fastapi import HTTPException

from tamanna_ai.api.routes import ChatRequest, chat


class FakeProvider:
    name = "ollama"

    def __init__(self, answer="Local model response"):
        self.generate = AsyncMock(return_value=answer)


class ChatRouteTests(unittest.IsolatedAsyncioTestCase):
    async def test_chat_uses_configured_local_provider(self):
        provider = FakeProvider()
        with patch("tamanna_ai.api.routes.get_model_provider", return_value=provider):
            result = await chat(ChatRequest(prompt="Explain photosynthesis"))
        self.assertEqual(result.response, "Local model response")
        self.assertEqual(result.provider, "ollama")
        provider.generate.assert_awaited_once_with("Explain photosynthesis")

    async def test_blank_prompt_is_rejected(self):
        with self.assertRaises(HTTPException) as raised:
            await chat(ChatRequest(prompt="   "))
        self.assertEqual(raised.exception.status_code, 422)


if __name__ == "__main__":
    unittest.main()
