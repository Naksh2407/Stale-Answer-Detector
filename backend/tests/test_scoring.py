"""Scoring tests for Stale-Answer Detector - offline, no LLM/Tavily credits needed."""
import sys
sys.path.insert(0, ".")
from app.scoring import score_claim, overall

def test_score_claim():
    assert score_claim("confirmed") == 100
    assert score_claim("unclear") == 50
    assert score_claim("contradicted") == 0
    assert score_claim("not_checked") is None  # excluded from average

def test_overall_all_confirmed():
    claims = [
        {"score": 100},
        {"score": 100},
    ]
    assert overall(claims) == 100

def test_overall_mixed():
    claims = [
        {"score": 100},
        {"score": 0},
    ]
    assert overall(claims) == 50

def test_overall_all_contradicted():
    claims = [
        {"score": 0},
        {"score": 0},
    ]
    assert overall(claims) == 0

def test_overall_no_scored():
    claims = [
        {"score": None},
        {"score": None},
    ]
    assert overall(claims) is None

def test_overall_empty():
    claims = []
    assert overall(claims) is None

def test_score_integration():
    # confirmed -> 100, contradicted -> 0, unclear -> 50
    claims = [
        {"verdict": "confirmed", "score": score_claim("confirmed")},
        {"verdict": "contradicted", "score": score_claim("contradicted")},
        {"verdict": "unclear", "score": score_claim("unclear")},
    ]
    scored = [c["score"] for c in claims if c["score"] is not None]
    avg = round(sum(scored) / len(scored))
    assert avg == 50  # (100 + 0 + 50) / 3 = 50

if __name__ == "__main__":
    test_score_claim()
    test_overall_all_confirmed()
    test_overall_mixed()
    test_overall_all_contradicted()
    test_overall_no_scored()
    test_overall_empty()
    test_score_integration()
    print("All scoring tests passed!")