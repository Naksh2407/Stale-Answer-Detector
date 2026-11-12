# Build, Install, and Run Instructions

This project verifies factual claims in AI-generated answers against live web sources.

## Prerequisites
- Python 3.10+
- A Bifrost API key and model (for LLM calls)
- A Tavily API key (for search)

## Setup
```bash
# 1. Install dependencies
cd backend
python -m venv .venv
source .venv/Scripts/activate
pip install -r requirements.txt

# 2. Configure environment
cp .env.example .env
# Edit .env and paste your TAVILY_API_KEY, BIFROST_URL, BIFROST_API_KEY, etc.

# 3. (Optional) Run offline demo mode (no credits needed)
# Set OFFLINE_MODE=1 in .env
```

## Running the project
```bash
# Start the Backend (API)
cd backend
source .venv/Scripts/activate
uvicorn app.main:app --reload --port 8000

# Start the Frontend (Simple Server)
cd ../frontend
python -m http.server 5500
# Then visit http://localhost:5500
```

## AI Usage Disclosure
- **At runtime**: A language model (via Bifrost) extracts claims and judges them against search snippets (via Tavily).
- **During development**: AI tools (Claude Code) were used for architecting, writing implementation code, generating testing fixtures, and documentation.

## License
MIT
