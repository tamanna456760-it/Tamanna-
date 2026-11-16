from __future__ import annotations

import json

import pytest

from scripts.index_github_repository_memory import (
    index_inventory,
    load_inventory,
    render_inventory,
)
from scripts.sync_github_repositories import build_inventory, build_public_inventory, write_inventory


def write_inventory(tmp_path, repositories):
    path = tmp_path / "github_repositories.json"
    path.write_text(json.dumps({
        "schema_version": 1,
        "generated_at": "2026-11-16T00:00:00+00:00",
        "repository_count": len(repositories),
        "repositories": repositories,
    }), encoding="utf-8")
    return path


def test_public_inventory_excludes_private_repository_names_and_descriptions():
    result = build_public_inventory([
        {"full_name": "owner/public", "private": False, "description": "Public project"},
        {"full_name": "owner/secret-project", "private": True, "description": "private marker"},
    ])

    assert result["repository_count"] == 1
    assert [item["full_name"] for item in result["repositories"]] == ["owner/public"]
    assert "secret-project" not in json.dumps(result)
    assert "private marker" not in json.dumps(result)


def test_private_inventory_requires_outside_repo_and_owner_only_permissions(tmp_path):
    repository_root = tmp_path / "checkout"
    repository_root.mkdir()
    items = [
        {"full_name": "owner/public", "private": False},
        {"full_name": "owner/private", "private": True, "description": "private marker"},
    ]
    inventory = build_inventory(items, include_private=True)
    assert inventory["repository_count"] == 2

    with pytest.raises(ValueError, match="absolute path"):
        write_inventory(inventory, "private.json", private=True, repo_root=repository_root)
    with pytest.raises(ValueError, match="outside the Git repository"):
        write_inventory(
            inventory,
            repository_root / "private.json",
            private=True,
            repo_root=repository_root,
        )

    symlink_target = tmp_path / "outside.json"
    symlink_target.write_text("{}", encoding="utf-8")
    symlink_path = tmp_path / "private-link.json"
    symlink_path.symlink_to(symlink_target)
    with pytest.raises(ValueError, match="symlink"):
        write_inventory(
            inventory, symlink_path, private=True, repo_root=repository_root
        )

    destination = tmp_path / "private-store" / "repositories.json"
    written = write_inventory(
        inventory, destination, private=True, repo_root=repository_root
    )
    assert written == destination
    assert written.stat().st_mode & 0o777 == 0o600
    assert "private marker" in written.read_text(encoding="utf-8")


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
