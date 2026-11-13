"""Bifrost client wrapper.

Every model call goes through complete(). Routing through Bifrost means the
provider, keys, and fallbacks are configured in the gateway, and this code
never changes.

In OFFLINE_MODE=1, reads saved responses from tests/fixtures/ instead of
calling Bifrost. This is how the demo and tests run with zero API credits,
which is essential for demo day and for sharing the project with teammates.

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
import re

from .config import settings
from . import fixtures

_client: object | None = None


def _get_client() -> object:
    global _client
    if _client is None:
        from openai import OpenAI
        _client = OpenAI(
            base_url=settings.bifrost_url,
            api_key=settings.bifrost_api_key or "not-set",
        )
    return _client


def complete(prompt: str, system: str | None = None, temperature: float = 0.0) -> str:
    if settings.offline:
        hit = fixtures.lookup_llm(prompt)
        if hit is not None:
            return hit

    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    resp = _get_client().chat.completions.create(
        model=settings.bifrost_model or "default-model",
        messages=messages,
        temperature=temperature,
        timeout=settings.request_timeout,
    )
    out = resp.choices[0].message.content or ""
    if not settings.offline:
        fixtures.record_llm(prompt, out)
    return out