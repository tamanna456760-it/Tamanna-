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


def test_search_response_reader_rejects_payload_over_limit():
    import asyncio

    class FakeResponse:
        def raise_for_status(self):
            return None

        async def aiter_bytes(self):
            yield b'{"results":'
            yield b'"' + (b"x" * safe_tools.MAX_SEARCH_RESPONSE_BYTES) + b'"}'

    with pytest.raises(safe_tools.ToolExecutionError, match="1 MB limit"):
        asyncio.run(safe_tools._read_limited_json(FakeResponse()))


def test_search_response_reader_parses_bounded_json():
    import asyncio

    class FakeResponse:
        def raise_for_status(self):
            return None

        async def aiter_bytes(self):
            yield b'{"results":[{"title":"safe"}]}'

    assert asyncio.run(safe_tools._read_limited_json(FakeResponse())) == {
        "results": [{"title": "safe"}]
    }


def test_execute_tool_audit_log_does_not_store_raw_error_details(tmp_path, monkeypatch):
    import asyncio
    import json

    log_path = tmp_path / "tool_calls.jsonl"
    monkeypatch.setattr(safe_tools, "LOG_PATH", log_path)

    async def fail_with_sensitive_detail(query):
        raise safe_tools.ToolExecutionError("provider echoed private-query-and-token")

    monkeypatch.setattr(safe_tools, "web_search", fail_with_sensitive_detail)
    with pytest.raises(safe_tools.ToolExecutionError):
        asyncio.run(safe_tools.execute_tool(
            "web_search",
            {"query": "private-query-and-token"},
        ))

    raw = log_path.read_text(encoding="utf-8")
    record = json.loads(raw)
    assert record["status"] == "error"
    assert record["error"] == "ToolExecutionError"
    assert "provider echoed private-query-and-token" not in raw
    assert "private-query-and-token" not in raw


def test_search_response_reader_rejects_malformed_json():
    import asyncio

    class FakeResponse:
        def raise_for_status(self):
            return None

        async def aiter_bytes(self):
            yield b'{"results": [invalid]}'

    with pytest.raises(safe_tools.ToolExecutionError, match="invalid JSON"):
        asyncio.run(safe_tools._read_limited_json(FakeResponse()))


def test_search_response_reader_checks_http_status_before_reading():
    import asyncio

    class FakeResponse:
        def raise_for_status(self):
            raise safe_tools.httpx.HTTPStatusError(
                "upstream failure",
                request=safe_tools.httpx.Request("GET", "https://provider.invalid"),
                response=safe_tools.httpx.Response(
                    503, request=safe_tools.httpx.Request("GET", "https://provider.invalid")
                ),
            )

        async def aiter_bytes(self):
            raise AssertionError("Body must not be read after an HTTP error")
            yield b""

    with pytest.raises(safe_tools.httpx.HTTPStatusError):
        asyncio.run(safe_tools._read_limited_json(FakeResponse()))


@pytest.mark.parametrize(
    "payload,provider",
    [
        (["not", "an", "object"], "tavily"),
        ({"results": "not-a-list"}, "tavily"),
        ({"results": ["not-an-object"]}, "tavily"),
        ({"web": []}, "brave"),
        ({"web": {"results": "not-a-list"}}, "brave"),
        ({"web": {"results": ["not-an-object"]}}, "brave"),
    ],
)
def test_search_result_extractor_rejects_invalid_shapes(payload, provider):
    with pytest.raises(safe_tools.ToolExecutionError, match="response shape"):
        safe_tools._extract_search_results(payload, provider)


def test_search_result_extractor_limits_results_to_five():
    payload = {"results": [{"title": str(index)} for index in range(8)]}
    assert len(safe_tools._extract_search_results(payload, "tavily")) == 5


def test_search_result_extractor_accepts_brave_response():
    payload = {"web": {"results": [{"title": "safe"}]}}
    assert safe_tools._extract_search_results(payload, "brave") == [{"title": "safe"}]


@pytest.mark.parametrize("failure_type", ["read_timeout", "connect_error"])
def test_web_search_translates_network_failures_without_leaking_details(
    monkeypatch, failure_type
):
    import asyncio

    request = safe_tools.httpx.Request("POST", "https://api.tavily.com/search")
    if failure_type == "read_timeout":
        failure = safe_tools.httpx.ReadTimeout("private-provider-detail", request=request)
    else:
        failure = safe_tools.httpx.ConnectError("private-provider-detail", request=request)

    class FailingStream:
        async def __aenter__(self):
            raise failure

        async def __aexit__(self, exc_type, exc, traceback):
            return False

    class FakeAsyncClient:
        def __init__(self, timeout):
            self.timeout = timeout

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, traceback):
            return False

        def stream(self, *args, **kwargs):
            return FailingStream()

    monkeypatch.setenv("TAMANNA_SEARCH_PROVIDER", "tavily")
    monkeypatch.setenv("TAVILY_API_KEY", "test-key-not-real")
    monkeypatch.setattr(safe_tools.httpx, "AsyncClient", FakeAsyncClient)

    with pytest.raises(safe_tools.ToolExecutionError) as exc_info:
        asyncio.run(safe_tools.web_search("test query"))

    assert failure_type.replace("_", "").lower() in type(failure).__name__.replace("_", "").lower()
    assert type(failure).__name__ in str(exc_info.value)
    assert "private-provider-detail" not in str(exc_info.value)


def test_web_search_rejects_query_outside_supported_length():
    import asyncio

    with pytest.raises(safe_tools.ToolInputError, match="1 to 500"):
        asyncio.run(safe_tools.web_search("x" * 501))
