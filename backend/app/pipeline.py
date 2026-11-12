import time
from .config import settings
from .extractor import extract_claims
from .verifier import verify
from .scoring import score_claim, overall

def run_check(answer: str) -> dict:
    start = time.time()
    claims = extract_claims(answer)
    searches_used = 0
    results = []

    for claim in claims:
        base = {
            "id": claim["id"], "type": claim["type"], "text": claim["text"],
            "span": claim["span"],
        }

        if claim["type"] not in ("pricing", "api_version"):
            results.append({**base, "score": None, "verdict": "not_checked",
                            "reason": "Not a pricing or API version claim (v1 scope).", "sources": []})
            continue

        if searches_used >= settings.max_searches:
            results.append({**base, "score": None, "verdict": "not_checked",
                            "reason": "Search limit reached for this request.", "sources": []})
            continue

        try:
            v = verify(claim)
            searches_used += 1
            results.append({
                **base,
                "score": score_claim(v["verdict"]),
                "verdict": v["verdict"],
                "reason": v["reason"],
                "current_value": v["current_value"],
                "sources": v["sources"],
            })
        except Exception as e:
            # One failed claim must not break the whole answer.
            results.append({**base, "score": None, "verdict": "not_checked",
                            "reason": f"Verification failed: {type(e).__name__}", "sources": []})

    return {
        "overall_freshness": overall(results),
        "claims": results,
        "timing_seconds": round(time.time() - start, 2),
    }