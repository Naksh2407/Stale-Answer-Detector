"""In-memory + on-disk history of every check performed.

Keeps a rolling log so the frontend can show "recent checks" and usage
stats without the backend losing state on restart. Stored as JSON lines
in a single file for simplicity; the last N entries are also kept in
memory for O(1) reads.
"""
import json
import os
import threading
import time
from typing import Any, Dict, List

from .config import settings

_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "history.json")
_MAX = 100
_lock = threading.Lock()
_cache: List[dict] = []


def _load() -> List[dict]:
    if not os.path.exists(_PATH):
        return []
    try:
        with open(_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        return []


def _save(data: List[dict]) -> None:
    try:
        with open(_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except OSError:
        pass  # history is best-effort


def _ensure() -> None:
    global _cache
    if not _cache:
        _cache = _load()


def record(answer: str, result: Dict[str, Any]) -> None:
    """Record one check. Trims to _MAX entries, newest first."""
    global _cache
    _ensure()
    with _lock:
        entry = {
            "id": f"#{len(_cache) + 1}",
            "ts": time.time(),
            "answer": answer[:400],
            "overall_freshness": result.get("overall_freshness"),
            "claims": result.get("claims", []),
            "timing_seconds": result.get("timing_seconds"),
        }
        _cache.insert(0, entry)
        if len(_cache) > _MAX:
            _cache = _cache[:_MAX]
        _save(_cache)


def recent(limit: int = 20) -> List[dict]:
    """Most recent checks, newest first. Each entry is trimmed for the
    frontend: short preview, verdict summary, freshness score."""
    _ensure()
    with _lock:
        out = []
        for e in _cache[:limit]:
            verdicts = [
                {"id": c.get("id"), "verdict": c.get("verdict"),
                 "score": c.get("score"), "text": c.get("text", "")[:80]}
                for c in e.get("claims", [])
            ]
            out.append({
                "id": e["id"],
                "ts": e["ts"],
                "preview": e["answer"][:120],
                "overall_freshness": e["overall_freshness"],
                "verdicts": verdicts,
                "timing_seconds": e["timing_seconds"],
            })
        return out


def stats() -> Dict[str, Any]:
    """Aggregate stats for the dashboard."""
    _ensure()
    with _lock:
        total = len(_cache)
        scored = [e for e in _cache if e.get("overall_freshness") is not None]
        avg = (round(sum(e["overall_freshness"] for e in scored) / len(scored))
               if scored else None)

        verdict_counts: Dict[str, int] = {}
        for e in _cache:
            for c in e.get("claims", []):
                v = c.get("verdict", "not_checked")
                verdict_counts[v] = verdict_counts.get(v, 0) + 1

        stale = sum(1 for e in _cache
                    if any(c.get("score") == 0 for c in e.get("claims", [])))
        fresh = sum(1 for e in _cache
                    if e.get("overall_freshness") == 100)

        return {
            "total_checks": total,
            "avg_freshness": avg,
            "fresh_answers": fresh,
            "stale_answers": stale,
            "verdict_counts": verdict_counts,
            "offline": settings.offline,
        }