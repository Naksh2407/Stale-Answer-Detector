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


def _find_span(answer: str, text: str):
    """Find the character span of `text` inside `answer`.

    Tries, in order:
      1. Exact substring match (fast path).
      2. Case-insensitive match.
      3. Whitespace-normalized match (the model may collapse spaces).
      4. Token-overlap match: the longest run of words from `text` that
         appears contiguously in `answer`. This handles paraphrasing where
         the model quotes part of the sentence but not the whole thing.
    """
    if not text:
        return None

    # 1. Exact
    start = answer.find(text)
    if start != -1:
        return [start, start + len(text)]

    # 2. Case-insensitive
    low = answer.lower()
    tlow = text.lower()
    start = low.find(tlow)
    if start != -1:
        return [start, start + len(text)]

    # 3. Whitespace-normalized
    def _norm(s: str) -> str:
        return re.sub(r"\s+", " ", s).strip()

    an = _norm(answer)
    tn = _norm(text)
    start = an.find(tn)
    if start != -1:
        # Map the normalized index back to the original answer's index.
        # Walk forward counting whitespace runs to find the real offset.
        ai, ni = 0, 0
        while ni < start and ai < len(answer):
            if answer[ai].isspace():
                while ai < len(answer) and answer[ai].isspace():
                    ai += 1
                if an[ni] == ' ':
                    ni += 1
            else:
                ai += 1
                ni += 1
        return [ai, ai + len(tn)]

    # 4. Token-overlap fallback: longest contiguous word run from `text`
    #    that appears in `answer`.
    words = re.findall(r"\S+", text)
    best_start, best_len = -1, 0
    for i in range(len(words)):
        for j in range(i + 1, len(words) + 1):
            run = " ".join(words[i:j])
            k = low.find(run.lower())
            if k != -1 and (j - i) > best_len:
                best_start, best_len = k, j - i
    if best_len >= 2:  # at least two words to avoid single-word noise
        return [best_start, best_start + len(" ".join(words[best_start:best_start + best_len]))]

    return None


def _derive_subject(text: str, claim_type: str) -> str:
    """Best-effort subject when the LLM omits one.

    The verifier builds a search query like "<subject> pricing", so a good
    subject matters. Heuristics:
      - "the X API" / "X API" -> X
      - "X plan" / "X pricing" -> X
      - Otherwise the first noun-ish chunk.
    """
    t = text.strip()
    m = re.search(r"(?:the\s+)?([A-Z][A-Za-z0-9\-]+)\s+API", t)
    if m:
        return m.group(1)
    m = re.search(r"([A-Z][A-Za-z0-9\-]+)\s+(?:plan|pricing|tier)", t)
    if m:
        return m.group(1)
    m = re.search(r"(?:the\s+)?([A-Z][A-Za-z0-9\-]+)", t)
    if m:
        return m.group(1)
    return t[:40]


def _normalize(items: list[dict], answer: str) -> list[dict]:
    """Turn raw LLM items into claims with ids, types, and spans."""
    claims = []
    for i, item in enumerate(items, start=1):
        text = str(item.get("text", "")).strip()
        if not text:
            continue
        raw_type = str(item.get("type", "other")).strip().lower()
        claim_type = raw_type if raw_type in _CLAIM_TYPES else "other"
        subject = str(item.get("subject", "")).strip() or _derive_subject(text, claim_type)
        span = _find_span(answer, text)

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