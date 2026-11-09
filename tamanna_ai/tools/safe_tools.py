"""Allow-listed, read-only tools for Tamanna AI."""
from __future__ import annotations
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import httpx

ROOT = Path(__file__).resolve().parents[2]
DOCS_DIR = ROOT / "data" / "docs"
LOG_PATH = ROOT / "logs" / "tool_calls.jsonl"
MAX_DOC_BYTES = 64 * 1024

class ToolInputError(ValueError):
    pass

class ToolConfigurationError(RuntimeError):
    pass

class ToolExecutionError(RuntimeError):
    pass

def _safe_log_value(value: Any) -> Any:
    if isinstance(value, str):
        return value[:240]
    if isinstance(value, (int, float, bool)) or value is None:
        return value
    if isinstance(value, dict):
        return {str(k)[:60]: _safe_log_value(v) for k, v in list(value.items())[:20]}
    if isinstance(value, list):
        return [_safe_log_value(v) for v in value[:20]]
    return type(value).__name__

def _log_call(name: str, arguments: dict[str, Any], status: str, error: str | None = None) -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    safe_arguments = dict(arguments)
    # Search queries may contain private user data; never persist their contents.
    if name == "web_search" and "query" in safe_arguments:
        safe_arguments["query"] = "[REDACTED]"
    for key in list(safe_arguments):
        if any(marker in str(key).lower() for marker in ("password", "secret", "token", "api_key", "authorization")):
            safe_arguments[key] = "[REDACTED]"
    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "tool": name,
        "arguments": _safe_log_value(safe_arguments),
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
                response = await client.post(
                    "https://api.tavily.com/search",
                    json={"api_key": key, "query": query, "max_results": 5, "search_depth": "basic"},
                )
                response.raise_for_status()
                data = response.json()
                return {"provider": "tavily", "results": data.get("results", [])[:5]}
            if provider == "brave":
                key = os.getenv("BRAVE_SEARCH_API_KEY", "").strip()
                if not key:
                    raise ToolConfigurationError("BRAVE_SEARCH_API_KEY is not configured")
                response = await client.get(
                    "https://api.search.brave.com/res/v1/web/search",
                    params={"q": query, "count": 5},
                    headers={"X-Subscription-Token": key, "Accept": "application/json"},
                )
                response.raise_for_status()
                data = response.json()
                return {"provider": "brave", "results": data.get("web", {}).get("results", [])[:5]}
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
        error = str(exc)
        raise
    finally:
        _log_call(name, arguments if isinstance(arguments, dict) else {}, status, error)

__all__ = [
    "ToolInputError", "ToolConfigurationError", "ToolExecutionError",
    "read_doc", "web_search", "execute_tool",
]
