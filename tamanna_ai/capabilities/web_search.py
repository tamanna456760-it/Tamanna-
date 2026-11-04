"""Optional real-time web search using the Brave Search API."""
from __future__ import annotations
import os
import httpx

class WebSearchError(RuntimeError):
    """Web search is unavailable or the provider rejected the request."""

class BraveSearchClient:
    """Bounded Brave Search client; requires BRAVE_SEARCH_API_KEY."""
    endpoint = "https://api.search.brave.com/res/v1/web/search"

    def __init__(self, api_key: str | None = None, timeout: float = 12.0):
        self.api_key = (api_key if api_key is not None else os.getenv("BRAVE_SEARCH_API_KEY", "")).strip()
        self.timeout = float(timeout)
        if self.timeout <= 0 or self.timeout > 30:
            raise ValueError("timeout must be between 0 and 30 seconds")

    async def search(self, query: str, *, limit: int = 5) -> list[dict[str, str]]:
        query = query.strip() if isinstance(query, str) else ""
        if not query or len(query) > 400:
            raise ValueError("query must contain 1 to 400 characters")
        if not 1 <= limit <= 10:
            raise ValueError("limit must be between 1 and 10")
        if not self.api_key:
            raise WebSearchError("BRAVE_SEARCH_API_KEY is not configured")
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    self.endpoint, params={"q": query, "count": limit},
                    headers={"X-Subscription-Token": self.api_key, "Accept": "application/json"},
                )
                response.raise_for_status()
                payload = response.json()
        except (httpx.HTTPError, ValueError) as exc:
            raise WebSearchError(f"Brave Search request failed: {type(exc).__name__}") from exc
        web = payload.get("web", {}) if isinstance(payload, dict) else {}
        results = web.get("results", []) if isinstance(web, dict) else []
        normalized = []
        for item in results[:limit] if isinstance(results, list) else []:
            if not isinstance(item, dict):
                continue
            title, url = item.get("title"), item.get("url")
            description = item.get("description", "")
            if isinstance(title, str) and isinstance(url, str) and url.startswith("https://"):
                normalized.append({
                    "title": title[:300], "url": url[:2000],
                    "description": description[:1500] if isinstance(description, str) else "",
                })
        return normalized

__all__ = ["BraveSearchClient", "WebSearchError"]
