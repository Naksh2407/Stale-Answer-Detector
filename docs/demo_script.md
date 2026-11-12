# Demo Script & Walkthrough

Welcome to the **Stale-Answer Detector** demo walkthrough! This project verifies time-sensitive claims (pricing and API versions) in LLM-generated responses against live web sources using **Bifrost** (AI gateway) and **Tavily** (live search).

## 2-Minute Demo Flow

### 1. Introduction (0:00 - 0:30)
- **The Problem:** LLMs have training cutoffs. When prices change or APIs deprecate, AI assistants continue presenting outdated information as fact.
- **Our Solution:** The Stale-Answer Detector extracts claims, verifies them via Tavily and Bifrost, scores them deterministically, and highlights freshness directly in the original answer.

### 2. Live Check Demonstration (0:30 - 1:15)
- Open `frontend/index.html` in your browser (or via Python HTTP server on port 5500).
- Paste the demo answer from `samples/stale_pricing.txt`:
  > *"The Pro plan costs $20 per month and includes 10GB of storage. The v2 API is the current version for this service."*
- Click **Check Freshness**.
- **Observe the Output:**
  - Overall freshness score calculated instantly (e.g., **50/100**).
  - The pricing claim is highlighted in **Red (Contradicted)**: *"Acme's pricing page lists the Pro plan at $30/month, not $20."* with the official pricing URL source link.
  - The API version claim is highlighted in **Green (Confirmed)**: *"Acme API docs state v2 is the current version."*

### 3. Architecture & Tech Stack Highlights (1:15 - 1:45)
- **Bifrost:** Manages all LLM orchestration for claim extraction and judging.
- **Tavily:** Powers live web research and source retrieval.
- **Deterministic Scorer:** Pure Python rules map verdicts (`confirmed` -> 100, `contradicted` -> 0, `unclear` -> 50) without LLM bias.
- **SQLite Cache & Offline Mode:** Zero-credit repeat runs and robust offline fixture testing.

### 4. Conclusion & Q&A (1:45 - 2:00)
- Ready for production use, hackathon evaluation, and expansion to regulation and company leadership claims in v2.
