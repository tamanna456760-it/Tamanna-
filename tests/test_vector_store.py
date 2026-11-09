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



def test_same_source_name_remains_isolated_across_owners_for_listing_and_deletion(tmp_path):
    store = VectorKnowledgeStore(fake_embedder, tmp_path / "tenant-sources.sqlite3")
    store.index_text(
        "Tamanna private security notes for account one",
        owner_id="user-1", source="notes.txt", title="Private notes one",
    )
    store.index_text(
        "Tamanna private database notes for account two",
        owner_id="user-2", source="notes.txt", title="Private notes two",
    )

    user_one_sources = store.list_sources(owner_id="user-1")
    user_two_sources = store.list_sources(owner_id="user-2")
    assert [item["title"] for item in user_one_sources] == ["Private notes one"]
    assert [item["title"] for item in user_two_sources] == ["Private notes two"]
    assert "chunk_text" not in user_one_sources[0]
    assert store.delete_source("notes.txt", owner_id="user-1") == 1
    assert store.search("database notes", owner_id="user-2")
    assert store.list_sources(owner_id="user-2")[0]["title"] == "Private notes two"


def test_reindex_only_recomputes_the_requested_owner(tmp_path):
    calls = []

    def tracking_embedder(text, task_type="RETRIEVAL_DOCUMENT"):
        calls.append(text)
        return fake_embedder(text, task_type)

    store = VectorKnowledgeStore(tracking_embedder, tmp_path / "tenant-reindex.sqlite3")
    store.index_text(
        "Tamanna security information for first user",
        owner_id="user-1", source="shared-name.txt",
    )
    store.index_text(
        "Tamanna database information for second user",
        owner_id="user-2", source="shared-name.txt",
    )
    calls.clear()

    result = store.reindex(owner_id="user-1")
    assert result == {"documents": 1, "chunks_reindexed": 1}
    assert len(calls) == 1
    assert "first user" in calls[0]
    assert "second user" not in calls[0]
    assert store.search("database information", owner_id="user-2")


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


def test_reindex_recomputes_existing_vectors_without_deleting_documents(tmp_path):
    old_embedder = lambda text, task_type="RETRIEVAL_DOCUMENT": [1.0, 0.0]
    new_embedder = lambda text, task_type="RETRIEVAL_DOCUMENT": [0.0, 1.0]
    db_path = tmp_path / "reindex.sqlite3"
    old_store = VectorKnowledgeStore(old_embedder, db_path)
    old_store.index_text(
        "Tamanna local semantic retrieval guide",
        owner_id="user-1", source="guide.md", title="Guide",
    )

    new_store = VectorKnowledgeStore(new_embedder, db_path)
    assert new_store.reindex(owner_id="user-1") == {
        "documents": 1, "chunks_reindexed": 1,
    }
    assert new_store.search("Tamanna local semantic retrieval guide",
                            owner_id="user-1")
    assert new_store.list_sources(owner_id="user-1")[0]["source"] == "guide.md"
    assert new_store.reindex(owner_id="user-2") == {
        "documents": 0, "chunks_reindexed": 0,
    }



def test_bengali_unicode_tokens_preserve_combining_marks_and_match_search(tmp_path):
    from tamanna_ai.knowledge.vector_store import LocalFeatureEmbedder

    store = VectorKnowledgeStore(LocalFeatureEmbedder(), tmp_path / "bengali.sqlite3")
    composed = "বাংলা ভাষার জ্ঞানভান্ডার"
    decomposed = "বা\u0982লা ভাষার জ্ঞানভান্ডার"
    assert store.index_text(
        composed, owner_id="user-bn", source="bengali.txt", title="বাংলা"
    ) == 1
    results = store.search(decomposed, owner_id="user-bn")
    assert results
    assert results[0]["source"] == "bengali.txt"
    assert results[0]["score"] > 0.5



def test_vector_store_rejects_invalid_embedding_vectors(tmp_path):
    import pytest
    from tamanna_ai.knowledge.vector_store import EmbeddingError

    for invalid in ([], [0.0, 0.0], [float("nan")], [float("inf")]):
        store = VectorKnowledgeStore(
            lambda text, task_type="RETRIEVAL_DOCUMENT": invalid,
            tmp_path / f"invalid-{len(invalid)}-{str(invalid[0] if invalid else 0)}.sqlite3",
        )
        with pytest.raises(EmbeddingError):
            store.index_text("private knowledge", owner_id="user-1", source="bad.txt")
        assert store.list_sources(owner_id="user-1") == []


def test_vector_store_rejects_invalid_query_embedding(tmp_path):
    import pytest
    from tamanna_ai.knowledge.vector_store import EmbeddingError

    store = VectorKnowledgeStore(
        lambda text, task_type="RETRIEVAL_DOCUMENT": [float("nan")],
        tmp_path / "invalid-query.sqlite3",
    )
    with pytest.raises(EmbeddingError):
        store.search("বাংলা প্রশ্ন", owner_id="user-1")



def test_bilingual_retrieval_benchmark_reports_ranking_metrics(tmp_path):
    from collections import Counter

    from scripts.benchmark_vector_retrieval import CASES, DOCUMENTS, evaluate
    from tamanna_ai.knowledge.vector_store import LocalFeatureEmbedder

    store = VectorKnowledgeStore(
        LocalFeatureEmbedder(), tmp_path / "evaluation.sqlite3"
    )
    for source, title, content in DOCUMENTS:
        store.index_text(
            content, owner_id="benchmark", source=source, title=title
        )

    report = evaluate(store, top_k=3)

    assert report["cases"] == len(DOCUMENTS)
    assert 0.0 <= report["hit_rate"] <= 1.0
    assert 0.0 <= report["mean_reciprocal_rank"] <= 1.0
    assert len(report["results"]) == len(DOCUMENTS)
    expected_language_counts = Counter(case["language"] for case in CASES)
    assert set(report["by_language"]) == set(expected_language_counts)
    for language, expected_count in expected_language_counts.items():
        assert report["by_language"][language]["cases"] == expected_count
    assert all("language" in result and "latency_ms" in result for result in report["results"])
