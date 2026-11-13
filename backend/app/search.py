"""Tavily search client wrapper.

One function: search(query, max_results) -> list[dict] with title, url, content.
Caching happens at this layer, so a repeated query costs zero credits.

In OFFLINE_MODE=1, reads saved results from tests/fixtures/ instead of
calling Tavily.

Note: an empty list means Tavily genuinely returned no results. Network and
auth errors raise, so the pipeline can mark the claim not_checked with a
clear reason instead of silently pretending the web has no information.
"""
import logging

from .config import settings
from . import cache, fixtures

log = logging.getLogger(__name__)

_tavily = None


def _get_tavily():
    global _tavily
    if _tavily is None:
        from tavily import TavilyClient
        _tavily = TavilyClient(api_key=settings.tavily_api_key or "not-set")
    return _tavily


def search(query: str, max_results: int = 5) -> list[dict]:
    cached = cache.get("search", query)
    if cached is not None:
        return cached

    if settings.offline:
        hit = fixtures.lookup_search(query)
        if hit is not None:
            return hit
        # No fixture for this query: return empty (verifier -> unclear).
        return []

    resp = _get_tavily().search(query=query, max_results=max_results)
    results = [
        {
            "title": r.get("title", ""),
            "url": r.get("url", ""),
            "content": r.get("content", ""),
            "published_date": r.get("published_date") or r.get("pub_date") or "Unknown"
        }
        for r in resp.get("results", [])
    ]
    cache.set("search", query, results)
    return results