from pathlib import Path

import pytest

from tamanna_ai.tools import safe_tools


def test_read_doc_rejects_parent_traversal_and_absolute_paths(tmp_path, monkeypatch):
    docs = tmp_path / "docs"
    docs.mkdir()
    outside = tmp_path / "secret.txt"
    outside.write_text("private", encoding="utf-8")
    monkeypatch.setattr(safe_tools, "DOCS_DIR", docs)

    with pytest.raises(safe_tools.ToolInputError):
        safe_tools.read_doc("../secret.txt")
    with pytest.raises(safe_tools.ToolInputError):
        safe_tools.read_doc(str(outside))


def test_read_doc_rejects_symlink_escape(tmp_path, monkeypatch):
    docs = tmp_path / "docs"
    docs.mkdir()
    outside = tmp_path / "outside.txt"
    outside.write_text("private", encoding="utf-8")
    link = docs / "linked.txt"
    try:
        link.symlink_to(outside)
    except (OSError, NotImplementedError):
        pytest.skip("Symlinks are unavailable on this platform")
    monkeypatch.setattr(safe_tools, "DOCS_DIR", docs)

    with pytest.raises(safe_tools.ToolInputError):
        safe_tools.read_doc("linked.txt")


def test_read_doc_allows_only_supported_files_and_enforces_size(tmp_path, monkeypatch):
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "notes.md").write_text("# Safe note", encoding="utf-8")
    (docs / "script.py").write_text("print('no')", encoding="utf-8")
    (docs / "large.txt").write_text("x" * (safe_tools.MAX_DOC_BYTES + 1), encoding="utf-8")
    monkeypatch.setattr(safe_tools, "DOCS_DIR", docs)

    assert safe_tools.read_doc("notes.md")["content"] == "# Safe note"
    with pytest.raises(safe_tools.ToolInputError):
        safe_tools.read_doc("script.py")
    with pytest.raises(safe_tools.ToolInputError):
        safe_tools.read_doc("large.txt")


def test_read_doc_rejects_empty_and_missing_paths(tmp_path, monkeypatch):
    docs = tmp_path / "docs"
    docs.mkdir()
    monkeypatch.setattr(safe_tools, "DOCS_DIR", docs)

    with pytest.raises(safe_tools.ToolInputError):
        safe_tools.read_doc(" ")
    with pytest.raises(safe_tools.ToolInputError):
        safe_tools.read_doc("missing.md")
