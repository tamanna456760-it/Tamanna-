
from tamanna_ai.knowledge.documentation_indexer import DocumentationIndexer


def test_documentation_index_and_search(tmp_path):
    (tmp_path / "README.md").write_text(
        "# Tamanna AI\nDocumentation search test",
        encoding="utf-8",
    )

    indexer = DocumentationIndexer(tmp_path)
    indexed = indexer.index()
    results = indexer.search("documentation search")

    assert len(indexed) == 1
    assert results[0]["path"] == "README.md"
    assert len(indexed[0]["sha256"]) == 64
