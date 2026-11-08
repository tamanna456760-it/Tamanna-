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
        with patch("tamanna_ai.api.routes.get_model_provider", return_value=provider), \
             patch("tamanna_ai.api.routes.require_user", return_value={"id": 42}), \
             patch("tamanna_ai.api.routes.VectorKnowledgeStore") as store:
            result = await chat(ChatRequest(prompt="Explain photosynthesis"))
        self.assertEqual(result.response, "Local model response")
        self.assertEqual(result.provider, "ollama")
        provider.generate.assert_awaited_once_with("Explain photosynthesis")
        self.assertEqual(store.return_value.search.call_count, 2)
        store.return_value.search.assert_any_call(
            "Explain photosynthesis", owner_id="user:42", limit=4
        )
        store.return_value.search.assert_any_call(
            "Explain photosynthesis", owner_id="tamanna-public", limit=4
        )

    async def test_model_status_lists_installed_models(self):
        with patch("tamanna_ai.api.routes.get_model_provider", return_value=FakeModelManager()):
            result = await model_status()
        self.assertEqual(result["status"], "ready")
        self.assertEqual(result["selected_model"], "qwen2.5:7b")
        self.assertTrue(result["selected_model_installed"])
        self.assertIn("llama3.2:3b", result["installed_models"])


    async def test_model_status_marks_missing_selected_model(self):
        manager = FakeModelManager()
        manager.client = type("ClientInfo", (), {"model": "qwen2.5:14b"})()
        with patch("tamanna_ai.api.routes.get_model_provider", return_value=manager):
            result = await model_status()
        self.assertEqual(result["status"], "ready")
        self.assertFalse(result["selected_model_installed"])

    async def test_model_status_reports_no_models_installed(self):
        manager = FakeModelManager()
        manager.list_models = AsyncMock(return_value=[])
        with patch("tamanna_ai.api.routes.get_model_provider", return_value=manager):
            result = await model_status()
        self.assertEqual(result["status"], "no_models_installed")
        self.assertFalse(result["selected_model_installed"])

    async def test_chat_includes_retrieved_context_as_untrusted_reference(self):
        provider = FakeProvider()
        with patch("tamanna_ai.api.routes.get_model_provider", return_value=provider), \
             patch("tamanna_ai.api.routes.require_user", return_value={"id": 42}), \
             patch("tamanna_ai.api.routes.VectorKnowledgeStore") as store:
            store.return_value.search.return_value = [{
                "source": "guide.md",
                "content": "Tamanna AI uses local inference.",
                "score": 0.9,
            }]
            await chat(ChatRequest(prompt="How does Tamanna work?"))
        sent_prompt = provider.generate.await_args.args[0]
        self.assertIn("<retrieved_context>", sent_prompt)
        self.assertIn("Tamanna AI uses local inference.", sent_prompt)
        self.assertIn("untrusted", sent_prompt)
        self.assertIn("How does Tamanna work?", sent_prompt)

    async def test_chat_can_disable_knowledge_retrieval(self):
        provider = FakeProvider()
        with patch("tamanna_ai.api.routes.get_model_provider", return_value=provider), \
             patch("tamanna_ai.api.routes.require_user", return_value={"id": 42}), \
             patch("tamanna_ai.api.routes.VectorKnowledgeStore") as store:
            await chat(ChatRequest(prompt="Hello", use_knowledge=False))
        store.assert_not_called()
        provider.generate.assert_awaited_once_with("Hello")


    async def test_chat_rejects_anonymous_user(self):
        with self.assertRaises(HTTPException) as raised:
            await chat(ChatRequest(prompt="Private question"))
        self.assertEqual(raised.exception.status_code, 401)

    async def test_package_app_mounts_signup_and_login_routes(self):
        from tamanna_ai.api.server import create_app
        paths = {route.path for route in create_app().routes}
        self.assertIn("/api/auth/signup", paths)
        self.assertIn("/api/auth/login", paths)
        self.assertIn("/tamanna-ai/chat", paths)

    async def test_blank_prompt_is_rejected(self):
        with self.assertRaises(HTTPException) as raised:
            await chat(ChatRequest(prompt="   "))
        self.assertEqual(raised.exception.status_code, 422)


if __name__ == "__main__":
    unittest.main()
