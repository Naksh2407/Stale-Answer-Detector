# Stale-Answer Detector — AI Truth & Freshness Diagnostics

[![FastAPI](https://img.shields.io/badge/FastAPI-0.100.0+-009688.svg?style=flat&logo=FastAPI&logoColor=white)](https://fastapi.tiangolo.com)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-3776AB.svg?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **Hackathon Edition**: A real-time verification diagnostic utility that detects stale, outdated, or hallucinated factual claims (pricing, API versions, deprecated features) in AI-generated answers against live web sources.

---

## ⚡ Quick Start (2-Minute Demo)

### Prerequisites
- **Python 3.10+** installed
- **Git Bash** (or POSIX-compatible terminal)

### 1-Click Setup & Launch
```bash
# Clone and enter directory
git clone https://github.com/your-username/stale-answer-detector.git
cd stale-answer-detector

# Run single startup script (launches API + Web UI)
python run_demo.py
```

- **Web Workspace**: `http://localhost:5500`
- **REST API Docs**: `http://localhost:8000/docs`

---

## 🌟 Key Features

| Feature | Description | Status |
| :--- | :--- | :---: |
| **🔍 Source Evidence Dates** | Displays exact publication/update timestamps for each web source. | ✅ Complete |
| **📊 Natural Language Summary** | Replaces raw numbers with clear narrative verdicts (e.g. *"2 of 3 checkable claims are out of date"*). | ✅ Complete |
| **✍️ Copy-Corrected Rewrite** | Generates an updated, accurate version of the answer with live values substituted. | ✅ Complete |
| **🎯 Multi-Source Verification** | Validates claims against multiple independent web sources for high confidence. | ✅ Complete |
| **🌐 URL Scraping & Audit** | Paste a link to any web page/AI answer to automatically extract and audit its contents. | ✅ Complete |
| **📂 Demo Preset Dropdown** | One-click loading of known-good samples (`Pricing`, `API Version`) running instantly offline. | ✅ Complete |
| **📜 Audit History & Telemetry** | Persistent session log with historical scores, claim breakdown, and live dashboard stats. | ✅ Complete |
| **🛡️ Not-Checked Clarity** | Clear visual badges explaining skipped claims (e.g. out of scope / unsupported). | ✅ Complete |
| **⚡ Bifrost Gateway Integration** | All LLM calls routed via Bifrost with automatic provider fallbacks and spending limits. | ✅ Complete |
| **🔒 Zero-Credit Offline Mode** | Full offline fixture replay for bulletproof hackathon presentations. | ✅ Complete |

---

## 🏗️ Architecture & Tech Stack

```
   ┌────────────────────────────────────────────────────────┐
   │                    Frontend Web UI                     │
   │      (Vanilla Modern JS, Design System, CSS Grid)     │
   └──────────────────────────┬─────────────────────────────┘
                              │ REST API
   ┌──────────────────────────▼─────────────────────────────┐
   │                     FastAPI Backend                    │
   │               (Pipeline, History, Scraper)             │
   └──────────────┬──────────────────────────┬──────────────┘
                  │                          │
   ┌──────────────▼──────────────┐  ┌────────▼──────────────┐
   │       Bifrost Gateway       │  │    Tavily Search API   │
   │ (LLM Extraction & Verifier) │  │  (Live Web Snippets)  │
   └─────────────────────────────┘  └───────────────────────┘
```

- **Backend**: FastAPI (Python), Pydantic v2, SQLite Caching, Requests (Scraper).
- **Frontend**: Vanilla JavaScript ES2022, Custom CSS Design System (Material 3 Dark Obsidian Theme), High-Contrast Typography (*Inter* + *JetBrains Mono*).
- **LLM Gateway**: **Bifrost** (Unified AI Gateway) for model routing, prompt fallbacks, and budget enforcement.
- **Search Provider**: **Tavily AI Search** for live web indexing and source date extraction.

---

## 🚀 Running Offline vs. Online

### 1. Offline Mode (Recommended for Demos & Testing)
In `backend/.env`, ensure:
```ini
OFFLINE_MODE=1
```
- **Zero API Credits required**.
- Uses recorded fixtures in `tests/fixtures/`.
- Guaranteed <10ms response times.
- Perfect for offline judging or live stage demos.

### 2. Live Web Mode
In `backend/.env`, set:
```ini
OFFLINE_MODE=0
BIFROST_URL=https://api.maximai.com/bifrost/v1
BIFROST_API_KEY=your-actual-bifrost-key
BIFROST_MODEL=gpt-4o
TAVILY_API_KEY=tvly-your-actual-tavily-key
```
Restart uvicorn:
```bash
cd backend
python -m uvicorn app.main:app --reload --port 8000
```

---

## 🧪 Testing

Run the automated Pytest suite (13/13 verified tests):

```bash
# Run pytest in offline mode
OFFLINE_MODE=1 PYTHONPATH=backend .venv/Scripts/python.exe -m pytest backend/tests
```

**Test Coverage:**
- `test_extractor.py`: Claim extraction, regex fallback, and span matching.
- `test_scoring.py`: Scoring engine rules (`confirmed` = 100, `unclear` = 50, `contradicted` = 0).
- `test_verifier.py`: Query builder, Tavily fixture matching, and verdict logic.

---

## 📖 REST API Reference

### `POST /check`
Execute an audit on text or URL.
```json
// Request
{
  "answer": "The Pro plan costs $20 per month.",
  "url": null
}

// Response
{
  "overall_freshness": 0,
  "summary_sentence": "1 of 1 checkable claim is out of date.",
  "corrected_answer": "The Pro plan costs $30 per month.",
  "claims": [
    {
      "id": "c1",
      "text": "The Pro plan costs $20 per month.",
      "type": "pricing",
      "verdict": "contradicted",
      "score": 0,
      "reason": "Acme's pricing page lists the Pro plan at $30/month.",
      "current_value": "$30/month",
      "sources": [
        {
          "title": "Acme Pricing Plans",
          "url": "https://acme.example.com/pricing",
          "published_date": "Updated November 2026"
        }
      ]
    }
  ],
  "timing_seconds": 0.02
}
```

### `GET /history`
Returns recent audits in the current session.

### `GET /stats`
Returns aggregate telemetry (total checks, mean freshness, stale flagged count).

### `GET /demo`
Instant demo response endpoint for one-click UI presentation.

---

## 🤖 AI Usage Disclosure

- **At Runtime**: **Bifrost** routes LLM completion calls for claim extraction, verdict judging, narrative summary, and copy-corrected rewrites. **Tavily** executes real-time web research and date retrieval.
- **During Development**: **Claude Code** (Anthropic) was used for architecture, frontend design system creation, test fixture generation, and API documentation.

---

## 📜 License

MIT License &copy; 2026 Nakshatra & Team.
Built for the AI Hackathon 2026.
