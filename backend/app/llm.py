"""Bifrost client wrapper.

Every model call goes through complete(). Routing through Bifrost means the
provider, keys, and fallbacks are configured in the gateway, and this code
never changes.

In OFFLINE_MODE=1, reads saved responses from tests/fixtures/ instead of
calling Bifrost. This is how the demo and tests run without spending credits.
"""
from openai import OpenAI
from .config import settings
from . import fixtures

_client: OpenAI | None = None


def _get_client() -> OpenAI:
    global _client
    if _client is None:
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