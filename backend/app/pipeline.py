import time
import json
from .config import settings
from .extractor import extract_claims
from .verifier import verify
from .scoring import score_claim, overall
from .llm import complete
from .prompts import SUMMARY_PROMPT, REWRITE_PROMPT

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
                            "reason": "Not a pricing or API version claim.", "sources": []})
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
            results.append({**base, "score": None, "verdict": "not_checked",
                            "reason": f"Verification failed: {type(e).__name__}", "sources": []})

    # Summary
    claims_json = json.dumps([{"text": c["text"], "verdict": c["verdict"]} for c in results if c["verdict"] != "not_checked"])
    try:
        summary = complete(SUMMARY_PROMPT.format(claims_json=claims_json))
    except Exception as e:
        summary = f"Audit completed. Overall freshness: {overall(results)}%"

    # Corrected Rewrite
    has_errors = any(c.get("verdict") == "contradicted" for c in results)
    corrected = None
    if has_errors:
        try:
            claims_data = json.dumps([{"text": c["text"], "verdict": c["verdict"], "current_value": c.get("current_value")} for c in results if c.get("current_value")])
            corrected = complete(REWRITE_PROMPT.format(answer=answer, claims_json=claims_data))
        except Exception as e:
            corrected = None

    return {
        "overall_freshness": overall(results),
        "summary_sentence": summary,
        "corrected_answer": corrected,
        "claims": results,
        "timing_seconds": round(time.time() - start, 2),
    }
