"""Allow-listed, read-only tools for Tamanna AI."""
from __future__ import annotations
import json
import ipaddress
import re
from html.parser import HTMLParser
import os
import math
from urllib.parse import urlsplit
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import httpx

ROOT = Path(__file__).resolve().parents[2]
DOCS_DIR = ROOT / "data" / "docs"
LOG_PATH = ROOT / "logs" / "tool_calls.jsonl"
MAX_DOC_BYTES = 64 * 1024
MAX_SEARCH_RESPONSE_BYTES = 1024 * 1024

class ToolInputError(ValueError):
    pass

class ToolConfigurationError(RuntimeError):
    pass

class ToolExecutionError(RuntimeError):
    pass

def _is_sensitive_log_key(key: Any) -> bool:
    normalized = str(key).lower().replace("-", "").replace("_", "").replace(" ", "")
    return any(marker in normalized for marker in (
        "password", "passwd", "secret", "token", "apikey", "authorization",
        "credential", "cookie", "session", "query",
    ))


def _safe_log_value(value: Any, key: Any = None) -> Any:
    if key is not None and _is_sensitive_log_key(key):
        return "[REDACTED]"
    if isinstance(value, str):
        return value[:240]
    if isinstance(value, (int, float, bool)) or value is None:
        return value
    if isinstance(value, dict):
        return {
            str(k)[:60]: _safe_log_value(v, k)
            for k, v in list(value.items())[:20]
        }
    if isinstance(value, list):
        return [_safe_log_value(item) for item in value[:20]]
    return type(value).__name__

def _log_call(name: str, arguments: dict[str, Any], status: str, error: str | None = None) -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    safe_arguments = _safe_log_value(arguments)
    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "tool": name,
        "arguments": safe_arguments,
        "status": status,
    }
    if error:
        record["error"] = error[:240]
    data = (json.dumps(record, ensure_ascii=False) + "\n").encode("utf-8")
    descriptor = os.open(str(LOG_PATH), os.O_APPEND | os.O_CREAT | os.O_WRONLY, 0o600)
    try:
        os.write(descriptor, data)
    finally:
        os.close(descriptor)

def read_doc(relative_path: str) -> dict[str, str]:
    if not isinstance(relative_path, str) or not relative_path.strip():
        raise ToolInputError("path is required")
    candidate = Path(relative_path)
    if candidate.is_absolute() or ".." in candidate.parts:
        raise ToolInputError("Only relative paths inside data/docs are allowed")
    docs_root = DOCS_DIR.resolve()
    try:
        target = (docs_root / candidate).resolve(strict=True)
        target.relative_to(docs_root)
    except (OSError, ValueError) as exc:
        raise ToolInputError("Document not found inside data/docs") from exc
    if not target.is_file() or target.suffix.lower() not in {".md", ".txt", ".json", ".csv", ".yaml", ".yml"}:
        raise ToolInputError("Only supported text documents can be read")
    if target.stat().st_size > MAX_DOC_BYTES:
        raise ToolInputError("Document exceeds the 64 KB read limit")
    try:
        return {"path": str(target.relative_to(docs_root)), "content": target.read_text(encoding="utf-8")}
    except (OSError, UnicodeError) as exc:
        raise ToolExecutionError("Document could not be read as UTF-8 text") from exc

async def _read_limited_json(response: httpx.Response) -> Any:
    response.raise_for_status()
    chunks: list[bytes] = []
    total = 0
    async for chunk in response.aiter_bytes():
        total += len(chunk)
        if total > MAX_SEARCH_RESPONSE_BYTES:
            raise ToolExecutionError("Search provider response exceeds the 1 MB limit")
        chunks.append(chunk)
    try:
        return json.loads(b"".join(chunks))
    except (ValueError, TypeError) as exc:
        raise ToolExecutionError("Search provider returned invalid JSON") from exc


class _SearchTextParser(HTMLParser):
    """Collect visible text while discarding markup and script/style contents."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self._hidden_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() in {"script", "style"}:
            self._hidden_depth += 1

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() in {"script", "style"} and self._hidden_depth:
            self._hidden_depth -= 1

    def handle_data(self, data: str) -> None:
        if not self._hidden_depth:
            self.parts.append(data)


def _sanitize_search_text(value: str, limit: int) -> str:
    parser = _SearchTextParser()
    try:
        parser.feed(value)
        parser.close()
        text = " ".join(parser.parts)
    except Exception:
        # Fail closed: never return unsanitized provider markup on parser errors.
        text = ""
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)
    return " ".join(text.split())[:limit]


def _extract_search_results(data: Any, provider: str) -> list[dict[str, Any]]:
    if not isinstance(data, dict):
        raise ToolExecutionError("Search provider returned an unexpected response shape")
    if provider == "tavily":
        results = data.get("results", [])
    elif provider == "brave":
        web_data = data.get("web", {})
        if not isinstance(web_data, dict):
            raise ToolExecutionError("Search provider returned an unexpected response shape")
        results = web_data.get("results", [])
    else:
        raise ToolConfigurationError("Unsupported search provider")
    if not isinstance(results, list) or any(not isinstance(item, dict) for item in results):
        raise ToolExecutionError("Search provider returned an unexpected response shape")

    safe_results: list[dict[str, Any]] = []
    for item in results[:5]:
        url = item.get("url")
        title = item.get("title")
        if not isinstance(url, str) or not isinstance(title, str):
            continue
        # Reject ambiguous raw URL characters before parsing. Encoded spaces remain valid.
        if len(url) > 2048 or any(
            character.isspace() or ord(character) < 0x20 or ord(character) == 0x7F
            for character in url
        ) or "\\" in url:
            continue
        try:
            parsed_url = urlsplit(url)
            hostname = parsed_url.hostname
            # Accessing .port validates its syntax and range (1..65535).
            port = parsed_url.port
            host_is_public = False
            if hostname:
                try:
                    address = ipaddress.ip_address(hostname)
                    host_is_public = address.is_global
                except ValueError:
                    try:
                        ascii_host = hostname.encode("idna").decode("ascii").lower()
                        labels = ascii_host.rstrip(".").split(".")
                        host_is_public = (
                            ascii_host not in {"localhost", "localhost.localdomain"}
                            and not ascii_host.endswith(".local")
                            and all(
                                label and len(label) <= 63
                                and re.fullmatch(r"[a-z0-9](?:[a-z0-9-]*[a-z0-9])?", label)
                                for label in labels
                            )
                        )
                    except UnicodeError:
                        host_is_public = False
            valid_url = (
                parsed_url.scheme.lower() in {"http", "https"}
                and host_is_public
                and parsed_url.username is None
                and parsed_url.password is None
                and not parsed_url.netloc.endswith(":")
                and (port is None or 1 <= port <= 65535)
            )
        except ValueError:
            valid_url = False
        if not valid_url:
            continue

        safe_item: dict[str, Any] = {
            "title": _sanitize_search_text(title, 300),
            "url": url,
        }
        text_field = item.get("content", item.get("description"))
        if isinstance(text_field, str):
            safe_item["content"] = _sanitize_search_text(text_field, 4000)
        score = item.get("score")
        if isinstance(score, (int, float)) and not isinstance(score, bool) and math.isfinite(score):
            safe_item["score"] = score
        safe_results.append(safe_item)
    return safe_results


async def web_search(query: str) -> dict[str, Any]:
    if not isinstance(query, str) or not query.strip() or len(query) > 500:
        raise ToolInputError("query must contain 1 to 500 characters")
    provider = os.getenv("TAMANNA_SEARCH_PROVIDER", "").strip().lower()
    timeout = httpx.Timeout(12.0, connect=5.0)
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            if provider == "tavily":
                key = os.getenv("TAVILY_API_KEY", "").strip()
                if not key:
                    raise ToolConfigurationError("TAVILY_API_KEY is not configured")
                async with client.stream(
                    "POST",
                    "https://api.tavily.com/search",
                    json={"api_key": key, "query": query, "max_results": 5, "search_depth": "basic"},
                ) as response:
                    data = await _read_limited_json(response)
                return {"provider": "tavily", "results": _extract_search_results(data, "tavily")}
            if provider == "brave":
                key = os.getenv("BRAVE_SEARCH_API_KEY", "").strip()
                if not key:
                    raise ToolConfigurationError("BRAVE_SEARCH_API_KEY is not configured")
                async with client.stream(
                    "GET",
                    "https://api.search.brave.com/res/v1/web/search",
                    params={"q": query, "count": 5},
                    headers={"X-Subscription-Token": key, "Accept": "application/json"},
                ) as response:
                    data = await _read_limited_json(response)
                return {"provider": "brave", "results": _extract_search_results(data, "brave")}
    except ToolConfigurationError:
        raise
    except httpx.HTTPError as exc:
        raise ToolExecutionError(f"Web search request failed: {type(exc).__name__}") from exc
    except (ValueError, TypeError) as exc:
        raise ToolExecutionError("Web search provider returned invalid data") from exc
    raise ToolConfigurationError("Set TAMANNA_SEARCH_PROVIDER to 'tavily' or 'brave' in .env")

async def execute_tool(name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    """Execute only the two explicitly allow-listed tools and log every attempt."""
    status = "error"
    error = None
    try:
        if not isinstance(arguments, dict):
            raise ToolInputError("arguments must be an object")
        if name == "read_doc":
            result = read_doc(str(arguments.get("path", "")))
        elif name == "web_search":
            result = await web_search(str(arguments.get("query", "")))
        else:
            raise ToolInputError("Tool is not allow-listed")
        status = "success"
        return {"ok": True, "tool": name, "result": result}
    except (ToolInputError, ToolConfigurationError, ToolExecutionError) as exc:
        # Error messages can include user input or provider details; logs keep only the class.
        error = type(exc).__name__
        raise
    finally:
        _log_call(name, arguments if isinstance(arguments, dict) else {}, status, error)

__all__ = [
    "ToolInputError", "ToolConfigurationError", "ToolExecutionError",
    "read_doc", "web_search", "execute_tool",
]
