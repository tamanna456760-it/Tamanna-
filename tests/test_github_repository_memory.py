from __future__ import annotations

import json

import pytest

from scripts.index_github_repository_memory import (
    index_inventory,
    load_inventory,
    render_inventory,
)


def write_inventory(tmp_path, repositories):
    path = tmp_path / "github_repositories.json"
    path.write_text(json.dumps({
        "schema_version": 1,
        "generated_at": "2026-11-16T00:00:00+00:00",
        "repository_count": len(repositories),
        "repositories": repositories,
    }), encoding="utf-8")
    return path


def test_load_inventory_deduplicates_and_allowlists_fields(tmp_path):
    path = write_inventory(tmp_path, [
        {
            "full_name": "owner/Project",
            "name": "Project",
            "owner": "owner",
            "private": True,
            "description": "Internal source",
            "access_token": "must-not-be-copied",
        },
        {"full_name": "OWNER/project", "description": "duplicate"},
    ])

    result = load_inventory(path)

    assert result["repository_count"] == 1
    assert result["repositories"][0]["full_name"] == "owner/Project"
    assert "access_token" not in result["repositories"][0]
    assert "must-not-be-copied" not in render_inventory(result)


def test_rejects_invalid_schema_and_bad_repository_entries(tmp_path):
    path = write_inventory(tmp_path, [{"full_name": "../invalid"}])
    with pytest.raises(ValueError, match="valid owner/name"):
        load_inventory(path)

    path.write_text('{"schema_version": 2, "repositories": []}', encoding="utf-8")
    with pytest.raises(ValueError, match="schema"):
        load_inventory(path)


def test_rejects_symlink_inventory(tmp_path):
    actual = write_inventory(tmp_path, [])
    link = tmp_path / "linked.json"
    link.symlink_to(actual)
    with pytest.raises(ValueError, match="non-symlink"):
        load_inventory(link)


def test_index_inventory_requires_owner_and_is_idempotent(tmp_path):
    inventory_path = write_inventory(tmp_path, [
        {
            "full_name": "owner/private-project",
            "name": "private-project",
            "owner": "owner",
            "private": True,
            "description": "Repository metadata for private owner",
        }
    ])
    inventory = load_inventory(inventory_path)
    database = tmp_path / "knowledge.sqlite3"

    with pytest.raises(ValueError, match="owner_id"):
        index_inventory(inventory, owner_id=" ", db_path=database)

    first = index_inventory(inventory, owner_id="admin-42", db_path=database)
    second = index_inventory(inventory, owner_id="admin-42", db_path=database)

    assert first >= 1
    assert second == first

    from tamanna_ai.knowledge.vector_store import LocalFeatureEmbedder, VectorKnowledgeStore
    store = VectorKnowledgeStore(LocalFeatureEmbedder(), db_path=database)
    assert store.search("private-project metadata", owner_id="admin-42")
    assert store.search("private-project metadata", owner_id="different-user") == []
