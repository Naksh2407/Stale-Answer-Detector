import os
from dotenv import load_dotenv

# Ensure we're in the right place
BASE = os.path.dirname(os.path.abspath(__file__))
os.chdir(os.path.join(BASE, "backend"))

print("Starting Stale-Answer Detector...")
print("1. Launching Backend (API)...")
os.system("start /B cmd /c \"..\\.venv\\Scripts\\activate && uvicorn app.main:app --port 8000\"")

print("2. Launching Frontend (Demo)...")
os.system("start /B cmd /c \"..\\.venv\\Scripts\\activate && cd ..\\frontend && python -m http.server 5500\"")

print("Backend: http://localhost:8000")
print("Frontend: http://localhost:5500")
print("Press Ctrl+C to stop.")
