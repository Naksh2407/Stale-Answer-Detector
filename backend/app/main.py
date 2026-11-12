from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from .pipeline import run_check
from .schemas import CheckRequest, CheckResponse

app = FastAPI(title="Stale-Answer Detector")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5500", "http://127.0.0.1:5500"],
    allow_methods=["POST", "GET"],
    allow_headers=["Content-Type"],
)

class CheckRequest(BaseModel):
    answer: str = Field(min_length=1, max_length=8000)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/check", response_model=CheckResponse)
def check(req: CheckRequest):
    try:
        return run_check(req.answer)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Pipeline failed: {type(e).__name__}")