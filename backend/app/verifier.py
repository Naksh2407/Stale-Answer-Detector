import json
from .llm import complete
from .search import search
from .prompts import JUDGE_SYSTEM, JUDGE_PROMPT
from . import cache

ALLOWED = {"confirmed", "unclear", "contradicted"}

def build_query(claim: dict) -> str:
    subject = claim.get("subject") or claim["text"]
    if claim["type"] == "pricing":
        return f"{subject} pricing"
    if claim["type"] == "api_version":
        return f"{subject} latest API version"
    return claim["text"]

def verify(claim: dict) -> dict:
    query = build_query(claim)
    try:
        snippets = search(query, max_results=5)
    except Exception:
        snippets = []

    if not snippets:
        return _verdict(claim, "unclear", None, "No current sources found for this claim.", [])

    cache_key = claim["text"] + "\n" + "\n".join(s["url"] for s in snippets)
    cached = cache.get("verdict", cache_key)
    if cached is not None:
        return {**cached, "claim_id": claim.get("id")}

    context = "\n\n".join(
        f"[{i}] {s['title']} ({s['url']})\n{s['content'][:1200]}"
        for i, s in enumerate(snippets)
    )
    prompt = JUDGE_PROMPT.format(claim=claim["text"], context=context)
    try:
        raw = complete(prompt, system=JUDGE_SYSTEM)
        cleaned = re_clean_json(raw)
        data = json.loads(cleaned)
        verdict = data.get("verdict", "unclear")
        if verdict not in ALLOWED:
            verdict = "unclear"
        reason = data.get("reason", "")
        current_value = data.get("current_value")
        used = [snippets[i] for i in data.get("source_indices", []) if 0 <= i < len(snippets)]
    except Exception:
        verdict, reason, current_value, used = "unclear", "Could not parse judge output or API error.", None, []

    result = _verdict(claim, verdict, current_value, reason, used)
    cache.set("verdict", cache_key, {k: v for k, v in result.items() if k != "claim_id"})
    return result

def re_clean_json(text: str) -> str:
    import re
    text = re.sub(r"```(?:json)?|```", "", text).strip()
    return text

def _verdict(claim, verdict, current_value, reason, sources):
    return {
        "claim_id": claim.get("id"),
        "verdict": verdict if verdict in ALLOWED else "unclear",
        "current_value": current_value,
        "reason": reason,
        "sources": [{"title": s["title"], "url": s["url"]} for s in sources],
    }
