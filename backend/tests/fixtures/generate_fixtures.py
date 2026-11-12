"""Generate offline fixtures for the demo answers.

Run with:  py -3 tests/fixtures/generate_fixtures.py

This computes the exact prompts the pipeline will send (using the same
templates in app/prompts.py), writes hand-authored LLM responses and Tavily
search results into llm_fixtures.json / search_fixtures.json, keyed by the
sha256 of the prompt/query. After this runs, OFFLINE_MODE=1 replays them.
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BACKEND = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, BACKEND)

from app.prompts import EXTRACT_PROMPT, JUDGE_PROMPT  # noqa: E402

SAMPLES = {
    "stale_pricing.txt": (
        "The Pro plan costs $20 per month and includes 10GB of storage. "
        "The v2 API is the current version for this service."
    ),
    "stale_api.txt": (
        "The latest version of the API is v1.0, which supports webhooks. "
        "The older v2 API has been deprecated."
    ),
}

# Hand-authored LLM responses for each sample answer.
EXTRACT_RESPONSES = {
    "stale_pricing.txt": [
        {"text": "The Pro plan costs $20 per month.", "type": "pricing", "subject": "Pro plan"},
        {"text": "includes 10GB of storage", "type": "other", "subject": "Pro plan"},
        {"text": "The v2 API is the current version for this service.", "type": "api_version", "subject": "v2 API"},
    ],
    "stale_api.txt": [
        {"text": "The latest version of the API is v1.0, which supports webhooks.", "type": "api_version", "subject": "API"},
        {"text": "The older v2 API has been deprecated.", "type": "api_version", "subject": "v2 API"},
    ],
}

# Hand-authored Tavily search results per query slug.
SEARCH_RESULTS = {
    "Pro plan pricing": [
        {
            "title": "Acme Pricing Plans",
            "url": "https://acme.example.com/pricing",
            "content": "Pro plan: $30 per month. Includes 10GB storage and priority support. Updated November 2026.",
        }
    ],
    "v2 API latest API version": [
        {
            "title": "Acme API Documentation",
            "url": "https://acme.example.com/docs/api",
            "content": "API v2 is the current version. v1 was deprecated in March 2026. The latest stable version is v2.",
        }
    ],
    "API latest API version": [
        {
            "title": "Acme API Documentation",
            "url": "https://acme.example.com/docs/api",
            "content": "The current API version is v3.0, released September 2026. v1.0 is deprecated. v2 is also deprecated.",
        }
    ],
}

# Hand-authored judge verdicts. Keyed by (claim_text, query_slug) for clarity.
JUDGE_RESPONSES = {
    ("The Pro plan costs $20 per month.", "Pro plan pricing"): {
        "verdict": "contradicted",
        "current_value": "$30/month",
        "reason": "Acme's pricing page lists the Pro plan at $30/month, not $20.",
        "source_indices": [0],
    },
    ("The v2 API is the current version for this service.", "v2 API latest API version"): {
        "verdict": "confirmed",
        "current_value": "v2",
        "reason": "Acme API docs state v2 is the current version.",
        "source_indices": [0],
    },
    ("The latest version of the API is v1.0, which supports webhooks.", "API latest API version"): {
        "verdict": "contradicted",
        "current_value": "v3.0",
        "reason": "Acme API docs list v3.0 as the current version; v1.0 is deprecated.",
        "source_indices": [0],
    },
    ("The older v2 API has been deprecated.", "v2 API latest API version"): {
        "verdict": "confirmed",
        "current_value": "v2 deprecated",
        "reason": "Acme API docs confirm v2 was deprecated in March 2026.",
        "source_indices": [0],
    },
}


def key(raw: str) -> str:
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def build_extract_prompt(answer: str) -> str:
    return EXTRACT_PROMPT.format(answer=answer, max_claims=10)


def build_judge_prompt(claim: str, snippets: list) -> str:
    context = "\n\n".join(
        f"[{i}] {s['title']} ({s['url']})\n{s['content'][:1200]}"
        for i, s in enumerate(snippets)
    )
    return JUDGE_PROMPT.format(claim=claim, context=context)


def main():
    llm_fixtures = {}
    search_fixtures = {}

    for fname, answer in SAMPLES.items():
        # Extract prompt -> response
        ep = build_extract_prompt(answer)
        llm_fixtures[key(ep)] = json.dumps(EXTRACT_RESPONSES[fname])

        # Claims from this answer, in order
        claims = EXTRACT_RESPONSES[fname]
        for claim in claims:
            if claim["type"] not in ("pricing", "api_version"):
                continue
            subject = claim.get("subject") or claim["text"]
            if claim["type"] == "pricing":
                query = f"{subject} pricing"
            else:
                query = f"{subject} latest API version"
            snippets = SEARCH_RESULTS.get(query, [])
            search_fixtures[key(query)] = snippets

            jp = build_judge_prompt(claim["text"], snippets)
            judge = JUDGE_RESPONSES.get((claim["text"], query))
            if judge is not None:
                llm_fixtures[key(jp)] = json.dumps(judge)

    os.makedirs(HERE, exist_ok=True)
    for name, data in (("llm_fixtures.json", llm_fixtures), ("search_fixtures.json", search_fixtures)):
        path = os.path.join(HERE, name)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"wrote {path} ({len(data)} entries)")


if __name__ == "__main__":
    main()