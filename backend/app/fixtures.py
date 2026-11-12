"""Offline fixture lookup.

When OFFLINE_MODE=1, llm.complete() and search.search() read saved responses
from tests/fixtures/ instead of calling Bifrost/Tavily. This lets the whole
pipeline run with zero API credits, which is essential for demo day and for
sharing the project with teammates.

Two lookup strategies, in order:
  1. Exact match on sha256 of the prompt/query (deterministic, recorded runs).
  2. Substring match: a fixture key that appears anywhere in the prompt/query.
     This makes fixtures work even before you've recorded the exact hash.

Fixtures are plain JSON files:
  tests/fixtures/llm_fixtures.json     -> { "<sha256 or slug>": "<model response>" }
  tests/fixtures/search_fixtures.json  -> { "<sha256 or slug>": [ {title,url,content}, ... ] }
"""
import hashlib
import json
import os
from typing import Any, Optional

FIXTURES_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "tests", "fixtures",
)

_LLM: dict = {}
_SEARCH: dict = {}


def _load(name: str) -> dict:
    path = os.path.join(FIXTURES_DIR, name)
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def _ensure_loaded() -> None:
    global _LLM, _SEARCH
    if not _LLM:
        _LLM = _load("llm_fixtures.json")
    if not _SEARCH:
        _SEARCH = _load("search_fixtures.json")


def _key(raw: str) -> str:
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _substring_match(d: dict, text: str) -> Optional[object]:
    """Prefer the LONGEST key that is a substring of `text`.

    Longest-match avoids collisions where a generic key (e.g. "API latest
    API version") would otherwise shadow a specific one (e.g. "v2 API
    latest API version") because the generic key is a substring of both.
    """
    best_val = None
    best_len = -1
    for slug, val in d.items():
        if slug and slug in text and len(slug) > best_len:
            best_val = val
            best_len = len(slug)
    return best_val


def lookup_llm(prompt: str) -> Optional[str]:
    """Return a saved LLM response for this prompt, or None."""
    _ensure_loaded()
    k = _key(prompt)
    if k in _LLM:
        return _LLM[k]
    return _substring_match(_LLM, prompt)


def lookup_search(query: str) -> Optional[list]:
    """Return saved search results for this query, or None."""
    _ensure_loaded()
    k = _key(query)
    if k in _SEARCH:
        return _SEARCH[k]
    return _substring_match(_SEARCH, query)


def record_llm(prompt: str, response: str) -> None:
    """Record a good LLM response so it can be replayed offline later."""
    _ensure_loaded()
    _LLM[_key(prompt)] = response
    _write("llm_fixtures.json", _LLM)


def record_search(query: str, results: list) -> None:
    _ensure_loaded()
    _SEARCH[_key(query)] = results
    _write("search_fixtures.json", _SEARCH)


def _write(name: str, data: dict) -> None:
    os.makedirs(FIXTURES_DIR, exist_ok=True)
    path = os.path.join(FIXTURES_DIR, name)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)