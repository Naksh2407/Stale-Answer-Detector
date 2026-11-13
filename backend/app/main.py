import json
import time
from typing import List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from .pipeline import run_check
from .schemas import CheckRequest, CheckResponse, BatchRequest, BatchResponse, DemoResponse
from . import history

app = FastAPI(title="Stale-Answer Detector")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class HealthResponse(BaseModel):
    status: str
    offline: bool
    version: str = "1.1.0"


@app.get("/health", response_model=HealthResponse)
def health():
    from .config import settings
    return {"status": "ok", "offline": settings.offline}


def _scrape_url(url: str) -> str:
    import requests
    import re
    from html.parser import HTMLParser

    class HTMLTextExtractor(HTMLParser):
        def __init__(self):
            super().__init__()
            self.text_chunks = []

        def handle_data(self, data):
            t = data.strip()
            if t:
                self.text_chunks.append(t)

    try:
        resp = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        if resp.status_code != 200:
            raise HTTPException(status_code=400, detail=f"Failed to fetch URL: HTTP {resp.status_code}")
        parser = HTMLTextExtractor()
        parser.feed(resp.text)
        text = " ".join(parser.text_chunks)
        if len(text) > 8000:
            text = text[:8000]
        return text
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"URL scraping failed: {e}")


@app.post("/check", response_model=CheckResponse)
def check(req: CheckRequest):
    answer = req.answer
    if not answer and req.url:
        answer = _scrape_url(req.url)
    if not answer:
        raise HTTPException(status_code=400, detail="Either 'answer' or 'url' must be provided.")

    try:
        result = run_check(answer)
        history.record(answer, result)
        return result
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Pipeline failed: {type(e).__name__}: {e}")


@app.post("/batch", response_model=BatchResponse)
def batch(req: BatchRequest):
    results = []
    for answer in req.answers:
        try:
            result = run_check(answer)
            history.record(answer, result)
            results.append({"answer": answer, **result})
        except Exception as e:
            results.append({
                "answer": answer,
                "overall_freshness": None,
                "claims": [],
                "timing_seconds": 0.0,
                "error": f"{type(e).__name__}: {e}",
            })
    return {"results": results, "count": len(results)}


@app.get("/demo", response_model=DemoResponse)
def demo():
    sample = (
        "The Pro plan costs $20 per month and includes 10GB of storage. "
        "The v2 API is the current version for this service."
    )
    try:
        result = run_check(sample)
        history.record(sample, result)
        return {"answer": sample, **result}
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Demo failed: {type(e).__name__}")


@app.get("/history")
def get_history(limit: int = 20):
    return {"entries": history.recent(limit)}


@app.get("/stats")
def get_stats():
    return history.stats()


@app.get("/fixtures")
def list_fixtures():
    from . import fixtures as fx
    fx._ensure_loaded()
    return {
        "llm_keys": list(fx._LLM.keys()),
        "search_keys": list(fx._SEARCH.keys()),
    }
