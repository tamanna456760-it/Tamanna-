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


def test_tool_audit_log_redacts_search_queries_and_secret_fields(tmp_path, monkeypatch):
    import json

    log_path = tmp_path / "tool_calls.jsonl"
    monkeypatch.setattr(safe_tools, "LOG_PATH", log_path)

    safe_tools._log_call(
        "web_search",
        {
            "query": "private medical or account details",
            "api_key": "do-not-store-this",
            "limit": 5,
        },
        "success",
    )

    record = json.loads(log_path.read_text(encoding="utf-8"))
    assert record["arguments"]["query"] == "[REDACTED]"
    assert record["arguments"]["api_key"] == "[REDACTED]"
    assert record["arguments"]["limit"] == 5
    assert "private medical or account details" not in log_path.read_text(encoding="utf-8")
    assert "do-not-store-this" not in log_path.read_text(encoding="utf-8")


def test_tool_audit_log_redacts_nested_queries_and_secret_key_variants(tmp_path, monkeypatch):
    import json

    log_path = tmp_path / "tool_calls.jsonl"
    monkeypatch.setattr(safe_tools, "LOG_PATH", log_path)

    safe_tools._log_call(
        "custom_tool",
        {
            "filters": {
                "query": "private nested search",
                "apiKey": "secret-api-key",
                "ordinary": "kept",
            },
            "session-token": "secret-session",
            "limit": 3,
        },
        "success",
    )

    raw = log_path.read_text(encoding="utf-8")
    record = json.loads(raw)
    assert record["arguments"]["filters"]["query"] == "[REDACTED]"
    assert record["arguments"]["filters"]["apiKey"] == "[REDACTED]"
    assert record["arguments"]["session-token"] == "[REDACTED]"
    assert record["arguments"]["filters"]["ordinary"] == "kept"
    assert record["arguments"]["limit"] == 3
    assert "private nested search" not in raw
    assert "secret-api-key" not in raw
    assert "secret-session" not in raw
