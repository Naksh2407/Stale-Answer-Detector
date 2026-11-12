"""Claim extraction.

Sends the answer to the LLM (via Bifrost) and parses a JSON array of claims.
Each claim is typed as pricing, api_version, or other, and carries its exact
character span in the original answer so the frontend can highlight it.

Graceful failure: if the LLM returns bad JSON twice, we return an empty list
rather than crashing the whole request.
"""
import json
import re

from .config import settings
from .llm import complete
from .prompts import EXTRACT_SYSTEM, EXTRACT_PROMPT
from . import cache

_CLAIM_TYPES = ("pricing", "api_version", "other")


def _parse_json_array(text: str) -> list[dict]:
    """Strip markdown fences and parse a JSON array from model output."""
    text = re.sub(r"```(?:json)?|```", "", text).strip()
    data = json.loads(text)
    if not isinstance(data, list):
        raise ValueError("expected a JSON array")
    return data


def _normalize(items: list[dict], answer: str) -> list[dict]:
    """Turn raw LLM items into claims with ids, types, and spans."""
    claims = []
    for i, item in enumerate(items, start=1):
        text = str(item.get("text", "")).strip()
        if not text:
            continue
        raw_type = str(item.get("type", "other")).strip().lower()
        claim_type = raw_type if raw_type in _CLAIM_TYPES else "other"
        subject = str(item.get("subject", "")).strip()

        # Span lets the frontend highlight the exact text. If the model
        # paraphrased instead of copying, span is None and the frontend
        # falls back to showing the claim in a list. That's graceful, not a bug.
        start = answer.find(text)
        span = [start, start + len(text)] if start != -1 else None

        claims.append({
            "id": f"c{i}",
            "text": text,
            "type": claim_type,
            "subject": subject,
            "span": span,
        })
    return claims


def extract_claims(answer: str) -> list[dict]:
    cached = cache.get("extract", answer)
    if cached is not None:
        return cached

    prompt = EXTRACT_PROMPT.format(answer=answer, max_claims=settings.max_claims)
    items: list[dict] = []
    last_error: Exception | None = None

    # One retry on bad JSON. Two failures -> empty list, not a crash.
    for attempt in range(2):
        try:
            raw = complete(prompt, system=EXTRACT_SYSTEM)
            items = _parse_json_array(raw)[: settings.max_claims]
            break
        except (json.JSONDecodeError, ValueError) as e:
            last_error = e
            continue

    claims = _normalize(items, answer)
    cache.set("extract", answer, claims)
    return claims