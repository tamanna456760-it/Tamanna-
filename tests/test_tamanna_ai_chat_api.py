import inspect
import unittest
from functools import wraps
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from fastapi import HTTPException

from tamanna_ai.api.routes import (
    model_resources, model_recovery, model_preflight, ChatRequest, KnowledgeImportRequest, ModelSelectRequest, ModelPullRequest, pull_model, select_model, system_metrics, model_benchmark, chat, delete_conversation,
    delete_knowledge, get_conversation, import_knowledge, list_conversations,
    list_knowledge, model_status, model_benchmark_history, MemoryRequest, create_memory, list_memories,
    update_memory, delete_memory,
)


# These tests call FastAPI endpoint functions directly rather than through ASGI.
# Supply the Request object that FastAPI normally injects; an empty Origin header
# represents a same-origin request and keeps the production origin check active.
def _with_test_request(route):
    if "request" not in inspect.signature(route).parameters:
        return route

    @wraps(route)
    async def invoke(*args, **kwargs):
        request = kwargs.get("request")
        if request is None or not hasattr(request, "headers"):
            kwargs["request"] = SimpleNamespace(headers={})
        return await route(*args, **kwargs)

    return invoke


for _route_name in (
    "pull_model", "select_model", "model_benchmark", "chat",
    "delete_conversation", "delete_knowledge", "import_knowledge",
    "create_memory", "update_memory", "delete_memory",
):
    globals()[_route_name] = _with_test_request(globals()[_route_name])


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
    def auth_patches(self, user_id=42):
        user = {"id": user_id, "email": f"user{user_id}@example.test", "name": f"User {user_id}"}
        return (
            patch("tamanna_ai.api.routes.require_user", return_value=user),
            patch("tamanna_ai.api.routes.database.ensure_user", return_value=user_id),
            patch("tamanna_ai.api.routes.database.load_history", return_value=[]),
            patch("tamanna_ai.api.routes.database.save_chat_pair"),
            patch("tamanna_ai.api.routes.database.list_memories", return_value=[]),
        )

    async def test_chat_uses_configured_local_provider_and_persists(self):
        provider = FakeProvider()
        auth, ensure, history, save, memories = self.auth_patches()
        with auth, ensure, history, save, memories as save_mock, patch("tamanna_ai.api.routes.get_model_provider", return_value=provider), patch("tamanna_ai.api.routes.VectorKnowledgeStore") as store:
            result = await chat(ChatRequest(prompt="Explain photosynthesis"))
        self.assertEqual(result.response, "Local model response")
        self.assertEqual(result.provider, "ollama")
        self.assertTrue(result.conversation_id)
        provider.generate.assert_awaited_once_with("Explain photosynthesis")
        store.return_value.search.assert_any_call("Explain photosynthesis", owner_id="user:42", limit=4)
        store.return_value.search.assert_any_call("Explain photosynthesis", owner_id="tamanna-public", limit=4)
        save_mock.assert_called_once()

    async def test_chat_reuses_conversation_and_includes_prior_turns(self):
        provider = FakeProvider()
        auth, ensure, _, save, memories = self.auth_patches(9)
        with auth, ensure, patch("tamanna_ai.api.routes.database.load_history", return_value=[{"user": "My name is Ali", "assistant": "Hello Ali"}]), save, memories, patch("tamanna_ai.api.routes.get_model_provider", return_value=provider):
            result = await chat(ChatRequest(prompt="What is my name?", use_knowledge=False, conversation_id="thread-9"))
        sent = provider.generate.await_args.args[0]
        self.assertIn("My name is Ali", sent)
        self.assertIn("Current user message: What is my name?", sent)
        self.assertEqual(result.conversation_id, "thread-9")


    async def test_chat_uses_private_saved_memories_as_context(self):
        provider = FakeProvider()
        auth, ensure, history, save, memories = self.auth_patches(15)
        with auth, ensure, history, save, memories as memory_mock, patch("tamanna_ai.api.routes.get_model_provider", return_value=provider), patch("tamanna_ai.api.routes.VectorKnowledgeStore"):
            memory_mock.return_value = ["User prefers Bengali responses"]
            await chat(ChatRequest(prompt="Explain this", use_knowledge=True))
        sent = provider.generate.await_args.args[0]
        self.assertIn("<user_memories>", sent)
        self.assertIn("User prefers Bengali responses", sent)


    async def test_chat_saves_only_explicit_remember_request_when_opted_in(self):
        provider = FakeProvider()
        auth, ensure, history, save, memories = self.auth_patches(22)
        with auth, ensure, history, save, memories, patch("tamanna_ai.api.routes.database.add_memory", return_value=88) as add, patch("tamanna_ai.api.routes.get_model_provider", return_value=provider), patch("tamanna_ai.api.routes.VectorKnowledgeStore"):
            await chat(ChatRequest(
                prompt="Please remember that I prefer short Bengali answers",
                use_knowledge=False, remember=True,
            ))
        add.assert_called_once_with(
            "I prefer short Bengali answers", user_id=22,
            metadata={"source": "explicit_chat_request", "kind": "user_memory"},
        )

    async def test_chat_does_not_auto_save_without_explicit_opt_in(self):
        provider = FakeProvider()
        auth, ensure, history, save, memories = self.auth_patches(23)
        with auth, ensure, history, save, memories, patch("tamanna_ai.api.routes.database.add_memory") as add, patch("tamanna_ai.api.routes.get_model_provider", return_value=provider):
            await chat(ChatRequest(
                prompt="Remember that I prefer concise answers",
                use_knowledge=False, remember=False,
            ))
        add.assert_not_called()

    async def test_model_benchmark_is_admin_only_and_returns_real_provider_metrics(self):
        expected = {
            "model": "qwen2.5:7b",
            "wall_time_ms": 120.5,
            "prompt_tokens": 20,
            "output_tokens": 35,
            "prompt_tokens_per_second": 100.0,
            "generation_tokens_per_second": 29.0,
            "total_duration_ms": 110.0,
            "model_load_ms": 10.0,
        }
        class BenchmarkProvider:
            name = "ollama"

            client = type("ClientInfo", (), {"model": "qwen2.5:7b"})()

            async def list_models(self):
                return ["qwen2.5:7b"]

            async def benchmark(self):
                return expected

        with patch("tamanna_ai.api.routes.check_origin"), patch(
            "tamanna_ai.api.routes.require_user",
            return_value={"id": 1, "email": "Tamanna456760@gmail.com"},
        ), patch("tamanna_ai.api.routes.get_model_provider", return_value=BenchmarkProvider()), patch(
            "tamanna_ai.api.routes.database.save_benchmark_run"
        ) as save_run:
            result = await model_benchmark(request=object(), token="admin-session")
        self.assertEqual(result, {"ok": True, "benchmark": expected, "scope": "single_local_inference"})
        save_run.assert_called_once_with(model="qwen2.5:7b", result=expected)

    async def test_model_resources_includes_installed_sizes_and_host_metrics(self):
        class ResourceProvider:
            name = "ollama"
            async def list_running_models(self):
                return []
            async def list_model_details(self):
                return [{"name": "qwen2.5:7b", "size_bytes": 4200}]
        host = {"memory": {"total_bytes": 16000, "used_bytes": 4000}, "gpu": {"available": False}}
        with patch("tamanna_ai.api.routes.require_user", return_value={
            "id": 1, "email": "Tamanna456760@gmail.com"
        }), patch("tamanna_ai.api.routes.get_model_provider", return_value=ResourceProvider()), patch(
            "tamanna_ai.api.routes.collect_system_metrics", new=AsyncMock(return_value=host)
        ):
            result = await model_resources(token="admin-session")
        self.assertEqual(result["installed_models"][0]["name"], "qwen2.5:7b")
        self.assertEqual(result["host"], host)

    async def test_model_resources_is_admin_only_and_returns_loaded_models(self):
        expected = [{
            "name": "qwen2.5:7b", "size_bytes": 4200000000,
            "memory_bytes": 3900000000, "expires_at": None,
            "context_length": 8192,
        }]
        class ResourceProvider:
            name = "ollama"

            async def list_running_models(self):
                return expected

            async def list_model_details(self):
                return [{"name": "qwen2.5:7b", "size_bytes": 4200000000}]

        host = {"memory": {"total_bytes": 10000, "used_bytes": 3000}, "gpu": {"available": False}}
        with patch("tamanna_ai.api.routes.require_user", return_value={
            "id": 1, "email": "Tamanna456760@gmail.com"
        }), patch("tamanna_ai.api.routes.get_model_provider", return_value=ResourceProvider()), patch(
            "tamanna_ai.api.routes.collect_system_metrics", new=AsyncMock(return_value=host)
        ):
            result = await model_resources(token="admin-session")
        self.assertEqual(result, {
            "ok": True, "models": expected, "count": 1,
            "installed_models": [{"name": "qwen2.5:7b", "size_bytes": 4200000000}],
            "host": host,
        })

    async def test_model_resources_denies_non_admin(self):
        with patch("tamanna_ai.api.routes.require_user", return_value={
            "id": 2, "email": "member@example.test"
        }), patch("tamanna_ai.api.routes.get_model_provider") as get_provider:
            with self.assertRaises(HTTPException) as raised:
                await model_resources(token="member-session")
        self.assertEqual(raised.exception.status_code, 403)
        get_provider.assert_not_called()

    async def test_benchmark_history_is_admin_only(self):
        expected = [{"id": 3, "model": "qwen2.5:7b", "result": {"passed_checks": 2}}]
        with patch("tamanna_ai.api.routes.require_user", return_value={
            "id": 1, "email": "Tamanna456760@gmail.com"
        }), patch("tamanna_ai.api.routes.database.list_benchmark_runs", return_value=expected) as history:
            result = await model_benchmark_history(limit=10, token="admin-session")
        self.assertEqual(result, {"runs": expected})
        history.assert_called_once_with(limit=10)

    async def test_benchmark_history_denies_non_admin(self):
        with patch("tamanna_ai.api.routes.require_user", return_value={
            "id": 2, "email": "member@example.test"
        }), patch("tamanna_ai.api.routes.database.list_benchmark_runs") as history:
            with self.assertRaises(HTTPException) as raised:
                await model_benchmark_history(token="member-session")
        self.assertEqual(raised.exception.status_code, 403)
        history.assert_not_called()

    async def test_model_benchmark_denies_non_admin(self):
        with patch("tamanna_ai.api.routes.check_origin"), patch(
            "tamanna_ai.api.routes.require_user",
            return_value={"id": 2, "email": "member@example.test"},
        ), patch("tamanna_ai.api.routes.get_model_provider") as get_provider:
            with self.assertRaises(HTTPException) as raised:
                await model_benchmark(request=object(), token="member-session")
        self.assertEqual(raised.exception.status_code, 403)
        get_provider.assert_not_called()

    async def test_system_metrics_requires_admin_and_returns_host_metrics(self):
        expected = {
            "cpu": {"usage_percent": 12.5, "logical_cores": 4},
            "memory": {"usage_percent": 40.0, "used_bytes": 400, "total_bytes": 1000},
            "disk": {"usage_percent": 50.0, "used_bytes": 500, "free_bytes": 500, "total_bytes": 1000},
            "gpu": {"available": False, "vendor": None, "utilization_percent": None,
                    "memory_used_mb": None, "memory_total_mb": None, "name": None},
        }
        with patch("tamanna_ai.api.routes.require_user", return_value={
            "id": 1, "email": "Tamanna456760@gmail.com"
        }), patch("tamanna_ai.api.routes.collect_system_metrics", return_value=expected) as collect:
            result = await system_metrics(token="admin-session")
        self.assertEqual(result, expected)
        collect.assert_awaited_once()

    async def test_system_metrics_denies_non_admin(self):
        with patch("tamanna_ai.api.routes.require_user", return_value={
            "id": 2, "email": "member@example.test"
        }), patch("tamanna_ai.api.routes.collect_system_metrics") as collect:
            with self.assertRaises(HTTPException) as raised:
                await system_metrics(token="member-session")
        self.assertEqual(raised.exception.status_code, 403)
        collect.assert_not_awaited()

    async def test_model_selection_is_admin_only(self):
        with patch("tamanna_ai.api.routes.check_origin"), patch(
            "tamanna_ai.api.routes.require_user",
            return_value={"id": 13, "email": "ordinary-user@example.test"},
        ), patch("tamanna_ai.api.routes.get_model_provider") as get_provider:
            with self.assertRaises(HTTPException) as raised:
                await select_model(
                    ModelSelectRequest(model="qwen2.5:7b"),
                    request=object(),
                    token="user-session",
                )
        self.assertEqual(raised.exception.status_code, 403)
        get_provider.assert_not_called()

    async def test_pull_model_streams_progress_after_authentication(self):
        class PullProvider:
            name = "ollama"

            async def pull_model(self, model):
                assert model == "qwen2.5:7b"
                yield {"status": "pulling", "completed": 50, "total": 100}

        with patch("tamanna_ai.api.routes.check_origin"), patch(
            "tamanna_ai.api.routes.require_user", return_value={"id": 12, "email": "Tamanna456760@gmail.com"}
        ), patch("tamanna_ai.api.routes.get_model_provider", return_value=PullProvider()):
            response = await pull_model(
                ModelPullRequest(model="qwen2.5:7b"),
                request=object(),
                token="session",
            )
        chunks = [chunk async for chunk in response.body_iterator]
        body = b"".join(chunk if isinstance(chunk, bytes) else chunk.encode() for chunk in chunks)
        self.assertIn(b'"status": "pulling"', body)
        self.assertIn(b'"completed": 50', body)
        self.assertIn(b'"done": true', body)

    async def test_model_preflight_reports_conservative_ram_estimate(self):
        class ResourceProvider:
            name = "ollama"
            async def list_model_details(self):
                return [{"name": "qwen2.5:7b", "size_bytes": 2 * 1024 ** 3}]
        host = {"memory": {"total_bytes": 16 * 1024 ** 3, "used_bytes": 2 * 1024 ** 3}}
        with patch("tamanna_ai.api.routes.check_origin"), patch(
            "tamanna_ai.api.routes.require_user", return_value={
                "id": 1, "email": "tamanna456760@gmail.com"
            }
        ), patch("tamanna_ai.api.routes.get_model_provider", return_value=ResourceProvider()), patch(
            "tamanna_ai.api.routes.collect_system_metrics", new=AsyncMock(return_value=host)
        ):
            result = await model_preflight(
                ModelSelectRequest(model="qwen2.5:7b"), request=object(), token="admin"
            )
        self.assertEqual(result["status"], "likely_fit")
        self.assertEqual(result["estimated_memory_bytes"], 4 * 1024 ** 3)
        self.assertFalse(result["selection_loads_model"])

    async def test_select_model_persists_only_an_installed_local_model(self):
        manager = FakeModelManager()
        with patch("tamanna_ai.api.routes.check_origin"), patch(
            "tamanna_ai.api.routes.require_user", return_value={"id": 12, "email": "tamanna456760@gmail.com"}
        ), patch("tamanna_ai.api.routes.get_model_provider", return_value=manager), patch(
            "tamanna_ai.api.routes.set_selected_model", return_value="llama3.2:3b"
        ) as save:
            result = await select_model(
                ModelSelectRequest(model="llama3.2:3b"), request=object(), token="session"
            )
        self.assertEqual(result["selected_model"], "llama3.2:3b")
        self.assertFalse(result["restart_required"])
        save.assert_called_once_with("llama3.2:3b")

    async def test_select_model_rejects_model_not_installed(self):
        with patch("tamanna_ai.api.routes.check_origin"), patch(
            "tamanna_ai.api.routes.require_user", return_value={"id": 12}
        ), patch("tamanna_ai.api.routes.get_model_provider", return_value=FakeModelManager()), patch(
            "tamanna_ai.api.routes.set_selected_model"
        ) as save:
            with self.assertRaises(HTTPException) as raised:
                await select_model(
                    ModelSelectRequest(model="not-installed:latest"),
                    request=object(), token="session",
                )
        self.assertEqual(raised.exception.status_code, 422)
        save.assert_not_called()

    async def test_model_recovery_reports_admin_runtime_diagnostics(self):
        class RecoveryProvider:
            name = "ollama"
            client = type("ClientInfo", (), {"model": "qwen2.5:7b"})()
            async def list_models(self):
                return ["qwen2.5:7b"]

        host = {"memory": {"usage_percent": 35}, "disk": {"usage_percent": 40}}
        with patch("tamanna_ai.api.routes.require_user", return_value={"id": 1, "email": "tamanna456760@gmail.com"}), patch(
            "tamanna_ai.api.routes.get_model_provider", return_value=RecoveryProvider()
        ), patch("tamanna_ai.api.routes.collect_system_metrics", new=AsyncMock(return_value=host)):
            result = await model_recovery(token="admin-session")
        self.assertEqual(result["status"], "healthy")
        self.assertEqual(result["code"], "runtime_available")
        self.assertFalse(result["automatic_changes"])

    async def test_model_recovery_denies_non_admin(self):
        with patch("tamanna_ai.api.routes.require_user", return_value={"id": 2, "email": "member@example.test"}):
            with self.assertRaises(HTTPException) as raised:
                await model_recovery(token="member-session")
        self.assertEqual(raised.exception.status_code, 403)

    async def test_model_status_lists_installed_models(self):
        with patch("tamanna_ai.api.routes.get_model_provider", return_value=FakeModelManager()):
            result = await model_status()
        self.assertEqual(result["status"], "ready")
        self.assertTrue(result["selected_model_installed"])

    async def test_model_status_reports_local_feature_embedding_provider(self):
        with patch("tamanna_ai.api.routes.get_model_provider", return_value=FakeModelManager()), patch(
            "tamanna_ai.api.routes.get_default_embedder",
            return_value=__import__("tamanna_ai.knowledge.vector_store", fromlist=["LocalFeatureEmbedder"]).LocalFeatureEmbedder(),
        ):
            result = await model_status()
        self.assertEqual(result["embedding"]["provider"], "local-feature")
        self.assertTrue(result["embedding"]["configured"])
        self.assertTrue(result["embedding"]["installed"])

    async def test_model_status_reports_ollama_embedding_installation(self):
        from tamanna_ai.knowledge.vector_store import OllamaEmbeddingProvider
        manager = FakeModelManager()
        manager.list_models = AsyncMock(return_value=[
            "qwen2.5:7b", "llama3.2:3b", "nomic-embed-text",
        ])
        with patch("tamanna_ai.api.routes.get_model_provider", return_value=manager), patch(
            "tamanna_ai.api.routes.get_default_embedder",
            return_value=OllamaEmbeddingProvider(model="nomic-embed-text"),
        ):
            result = await model_status()
        self.assertEqual(result["embedding"]["provider"], "ollama")
        self.assertTrue(result["embedding"]["installed"])


    async def test_model_status_marks_missing_selected_model(self):
        manager = FakeModelManager()
        manager.client = type("ClientInfo", (), {"model": "qwen2.5:14b"})()
        with patch("tamanna_ai.api.routes.get_model_provider", return_value=manager):
            result = await model_status()
        self.assertFalse(result["selected_model_installed"])

    async def test_model_status_reports_no_models_installed(self):
        manager = FakeModelManager()
        manager.list_models = AsyncMock(return_value=[])
        with patch("tamanna_ai.api.routes.get_model_provider", return_value=manager):
            result = await model_status()
        self.assertEqual(result["status"], "no_models_installed")

    async def test_chat_includes_retrieved_context_as_untrusted_reference(self):
        provider = FakeProvider()
        auth, ensure, history, save, memories = self.auth_patches()
        with auth, ensure, history, save, memories, patch("tamanna_ai.api.routes.get_model_provider", return_value=provider), patch("tamanna_ai.api.routes.VectorKnowledgeStore") as store:
            store.return_value.search.return_value = [{"source": "guide.md", "content": "Tamanna AI uses local inference.", "score": 0.9}]
            await chat(ChatRequest(prompt="How does Tamanna work?"))
        sent = provider.generate.await_args.args[0]
        self.assertIn("<retrieved_context>", sent)
        self.assertIn("untrusted", sent)
        self.assertIn("How does Tamanna work?", sent)

    async def test_chat_can_disable_knowledge_retrieval(self):
        provider = FakeProvider()
        auth, ensure, history, save, memories = self.auth_patches()
        with auth, ensure, history, save, memories, patch("tamanna_ai.api.routes.get_model_provider", return_value=provider), patch("tamanna_ai.api.routes.VectorKnowledgeStore") as store:
            await chat(ChatRequest(prompt="Hello", use_knowledge=False))
        store.assert_not_called()
        provider.generate.assert_awaited_once_with("Hello")

    async def test_chat_rejects_anonymous_user(self):
        with self.assertRaises(HTTPException) as raised:
            await chat(ChatRequest(prompt="Private question"))
        self.assertEqual(raised.exception.status_code, 401)

    async def test_package_app_mounts_auth_chat_and_conversation_routes(self):
        from tamanna_ai.api.server import create_app
        paths = set(create_app().openapi()["paths"])
        self.assertIn("/api/auth/signup", paths)
        self.assertIn("/api/auth/login", paths)
        self.assertIn("/tamanna-ai/chat", paths)
        self.assertIn("/tamanna-ai/conversations", paths)

    async def test_private_knowledge_import_uses_authenticated_owner(self):
        with patch("tamanna_ai.api.routes.require_user", return_value={"id": 7}), patch("tamanna_ai.api.routes.VectorKnowledgeStore") as store:
            result = await import_knowledge(KnowledgeImportRequest(filename="notes.md", content="# Private notes"))
        self.assertTrue(result["ok"])
        store.return_value.index_text.assert_called_once_with("# Private notes", owner_id="user:7", source="notes.md", title="notes")

    async def test_private_knowledge_import_rejects_path_traversal(self):
        with patch("tamanna_ai.api.routes.require_user", return_value={"id": 7}):
            with self.assertRaises(HTTPException) as raised:
                await import_knowledge(KnowledgeImportRequest(filename="../private.md", content="text"))
        self.assertEqual(raised.exception.status_code, 422)

    async def test_private_knowledge_import_rejects_invalid_json(self):
        with patch("tamanna_ai.api.routes.require_user", return_value={"id": 7}):
            with self.assertRaises(HTTPException) as raised:
                await import_knowledge(KnowledgeImportRequest(filename="data.json", content="{bad json"))
        self.assertEqual(raised.exception.status_code, 422)

    async def test_list_knowledge_is_user_scoped(self):
        with patch("tamanna_ai.api.routes.require_user", return_value={"id": 12}), patch("tamanna_ai.api.routes.VectorKnowledgeStore") as store:
            store.return_value.list_sources.return_value = [{"source": "mine.md"}]
            result = await list_knowledge()
        store.return_value.list_sources.assert_called_once_with(owner_id="user:12")
        self.assertEqual(result["documents"], [{"source": "mine.md"}])

    async def test_delete_knowledge_is_user_scoped(self):
        with patch("tamanna_ai.api.routes.require_user", return_value={"id": 12}), patch("tamanna_ai.api.routes.VectorKnowledgeStore") as store:
            store.return_value.delete_source.return_value = 2
            result = await delete_knowledge("mine.md")
        store.return_value.delete_source.assert_called_once_with("mine.md", owner_id="user:12")
        self.assertEqual(result["chunks_deleted"], 2)

    async def test_list_conversations_is_user_scoped(self):
        with patch("tamanna_ai.api.routes.require_user", return_value={"id": 4, "email": "four@example.test", "name": "Four"}), patch("tamanna_ai.api.routes.database.ensure_user", return_value=4), patch("tamanna_ai.api.routes.database.list_conversations", return_value=[{"id": "mine"}]) as listing:
            result = await list_conversations()
        listing.assert_called_once_with(user_id=4, limit=50)
        self.assertEqual(result["conversations"], [{"id": "mine"}])

    async def test_get_conversation_is_user_scoped(self):
        with patch("tamanna_ai.api.routes.require_user", return_value={"id": 4, "email": "four@example.test", "name": "Four"}), patch("tamanna_ai.api.routes.database.ensure_user", return_value=4), patch("tamanna_ai.api.routes.database.load_history", return_value=[{"user": "Hi", "assistant": "Hello"}]) as load:
            result = await get_conversation("mine", token="session")
        load.assert_called_once_with(conversation_id="mine", user_id=4, limit_pairs=100)
        self.assertEqual(len(result["messages"]), 1)

    async def test_delete_conversation_is_user_scoped(self):
        with patch("tamanna_ai.api.routes.require_user", return_value={"id": 4, "email": "four@example.test", "name": "Four"}), patch("tamanna_ai.api.routes.database.ensure_user", return_value=4), patch("tamanna_ai.api.routes.database.delete_conversation", return_value=True) as delete:
            result = await delete_conversation("mine", token="session")
        delete.assert_called_once_with("mine", user_id=4)
        self.assertTrue(result["ok"])


    async def test_create_memory_uses_authenticated_user(self):
        with patch("tamanna_ai.api.routes.require_user", return_value={"id": 6, "email": "six@example.test", "name": "Six"}), patch("tamanna_ai.api.routes.database.ensure_user", return_value=6), patch("tamanna_ai.api.routes.database.add_memory", return_value=31) as add:
            result = await create_memory(MemoryRequest(content="Prefers Bengali"))
        add.assert_called_once_with("Prefers Bengali", user_id=6, metadata={"source": "user"})
        self.assertEqual(result["memory"]["id"], 31)

    async def test_list_memories_is_user_scoped(self):
        with patch("tamanna_ai.api.routes.require_user", return_value={"id": 6, "email": "six@example.test", "name": "Six"}), patch("tamanna_ai.api.routes.database.ensure_user", return_value=6), patch("tamanna_ai.api.routes.database.list_memory_records", return_value=[{"id": 31, "content": "Private"}]) as listing:
            result = await list_memories()
        listing.assert_called_once_with(user_id=6, limit=200)
        self.assertEqual(result["memories"][0]["id"], 31)

    async def test_update_memory_is_user_scoped(self):
        with patch("tamanna_ai.api.routes.require_user", return_value={"id": 6, "email": "six@example.test", "name": "Six"}), patch("tamanna_ai.api.routes.database.ensure_user", return_value=6), patch("tamanna_ai.api.routes.database.update_memory", return_value=True) as update:
            result = await update_memory(31, MemoryRequest(content="Updated preference"))
        update.assert_called_once_with(31, "Updated preference", user_id=6)
        self.assertTrue(result["ok"])

    async def test_delete_memory_is_user_scoped(self):
        with patch("tamanna_ai.api.routes.require_user", return_value={"id": 6, "email": "six@example.test", "name": "Six"}), patch("tamanna_ai.api.routes.database.ensure_user", return_value=6), patch("tamanna_ai.api.routes.database.delete_memory", return_value=True) as delete:
            result = await delete_memory(31)
        delete.assert_called_once_with(31, user_id=6)
        self.assertTrue(result["ok"])

    async def test_blank_prompt_is_rejected(self):
        with self.assertRaises(HTTPException) as raised:
            await chat(ChatRequest(prompt="   "))
        self.assertEqual(raised.exception.status_code, 422)


if __name__ == "__main__":
    unittest.main()
