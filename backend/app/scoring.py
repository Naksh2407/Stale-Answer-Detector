SCORES = {"confirmed": 100, "unclear": 50, "contradicted": 0}

def score_claim(verdict: str) -> int | None:
    return SCORES.get(verdict)  # None for not_checked

def overall(claims: list[dict]) -> int | None:
    scored = [c["score"] for c in claims if c["score"] is not None]
    if not scored:
        return None
    return round(sum(scored) / len(scored))
