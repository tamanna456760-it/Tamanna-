from tamanna_ai.knowledge.vector_store import VectorKnowledgeStore, chunk_text


def fake_embedder(text, task_type="RETRIEVAL_DOCUMENT"):
    words = set(text.lower().split())
    vocabulary = ["tamanna", "security", "memory", "database", "recipe"]
    return [float(word in words) for word in vocabulary]


def test_chunk_text_respects_limit_and_overlap():
    text = ("alpha " * 250) + "\n\n" + ("beta " * 250)
    chunks = chunk_text(text, max_chars=300, overlap=40)
    assert chunks
    assert all(len(chunk) <= 300 for chunk in chunks)


def test_vector_store_persists_and_isolates_owners(tmp_path):
    store = VectorKnowledgeStore(fake_embedder, tmp_path / "vectors.sqlite3")
    assert store.index_text(
        "Tamanna security database memory", owner_id="user-1",
        source="guide.txt", title="Security guide",
    ) == 1
    assert store.search("security memory", owner_id="user-1")[0]["source"] == "guide.txt"
    assert store.search("security memory", owner_id="user-2") == []
    assert store.delete_source("guide.txt", owner_id="user-2") == 0
    assert store.delete_source("guide.txt", owner_id="user-1") == 1


def test_vector_store_requires_owner_and_limits_document_size(tmp_path):
    store = VectorKnowledgeStore(fake_embedder, tmp_path / "vectors.sqlite3", max_file_bytes=1024)
    import pytest
    with pytest.raises(ValueError):
        store.index_text("private content", owner_id="", source="a.txt")
    with pytest.raises(ValueError):
        store.index_text("x" * 2048, owner_id="user-1", source="large.txt")



def test_local_feature_embedder_is_deterministic_and_normalized():
    from tamanna_ai.knowledge import LocalFeatureEmbedder

    embedder = LocalFeatureEmbedder()
    first = embedder("Tamanna local memory security")
    second = embedder("Tamanna local memory security")
    assert len(first) == 384
    assert first == second
    assert abs(sum(value * value for value in first) - 1.0) < 1e-9


def test_vector_store_uses_local_embedder_without_api_configuration(tmp_path, monkeypatch):
    from tamanna_ai.knowledge import LocalFeatureEmbedder

    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    store = VectorKnowledgeStore(db_path=tmp_path / "local.sqlite3")
    assert isinstance(store.embedder, LocalFeatureEmbedder)
    assert store.index_text(
        "Tamanna local security memory", owner_id="owner-a",
        source="local.txt", title="Local notes",
    ) == 1
    matches = store.search("security memory", owner_id="owner-a")
    assert matches
    assert matches[0]["source"] == "local.txt"


def test_hybrid_search_ranks_documents_with_more_query_context_first(tmp_path):
    store = VectorKnowledgeStore(fake_embedder, tmp_path / "hybrid.sqlite3")
    store.index_text(
        "Security controls protect the application and database.",
        owner_id="user-1", source="security.md", title="Security",
    )
    store.index_text(
        "Memory persistence stores private conversation memory securely.",
        owner_id="user-1", source="memory.md", title="Memory",
    )
    store.index_text(
        "Security and memory are both covered by this combined guide.",
        owner_id="user-1", source="combined.md", title="Combined",
    )

    results = store.search("security memory", owner_id="user-1", limit=3)

    assert results[0]["source"] == "combined.md"
    assert results[0]["score"] > results[1]["score"]
    assert all(0.0 <= result["score"] <= 1.0 for result in results)


def test_ollama_embedding_provider_uses_local_embed_endpoint():
    import httpx
    from unittest.mock import patch
    from tamanna_ai.knowledge.vector_store import OllamaEmbeddingProvider

    class FakeClient:
        request_data = None

        def __init__(self, timeout=None):
            self.timeout = timeout

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def post(self, url, json):
            type(self).request_data = (url, json)
            return httpx.Response(
                200, json={"embeddings": [[3.0, 4.0]]},
                request=httpx.Request("POST", url),
            )

    with patch("tamanna_ai.knowledge.vector_store.httpx.Client", FakeClient):
        vector = OllamaEmbeddingProvider(
            base_url="http://127.0.0.1:11434", model="nomic-embed-text"
        )("meaning of life", task_type="RETRIEVAL_QUERY")

    assert vector == [0.6, 0.8]
    url, payload = FakeClient.request_data
    assert url == "http://127.0.0.1:11434/api/embed"
    assert payload == {"model": "nomic-embed-text", "input": "meaning of life"}


def test_embedding_provider_selection_is_local_and_configurable(tmp_path, monkeypatch):
    from tamanna_ai.knowledge.vector_store import (
        LocalFeatureEmbedder, OllamaEmbeddingProvider,
    )

    monkeypatch.delenv("TAMANNA_EMBEDDING_PROVIDER", raising=False)
    assert isinstance(VectorKnowledgeStore(db_path=tmp_path / "default.sqlite").embedder,
                      LocalFeatureEmbedder)
    monkeypatch.setenv("TAMANNA_EMBEDDING_PROVIDER", "ollama")
    monkeypatch.setenv("TAMANNA_EMBEDDING_MODEL", "nomic-embed-text")
    assert isinstance(VectorKnowledgeStore(db_path=tmp_path / "ollama.sqlite").embedder,
                      OllamaEmbeddingProvider)
