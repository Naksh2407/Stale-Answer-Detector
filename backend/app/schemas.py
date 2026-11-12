from pydantic import BaseModel, Field
from typing import List, Optional

class Source(BaseModel):
    title: str
    url: str

class Claim(BaseModel):
    id: str
    text: str
    type: str  # pricing, api_version, other
    span: Optional[List[int]] = None
    subject: Optional[str] = None

class VerifiedClaim(Claim):
    score: Optional[int] = None
    verdict: str  # confirmed, unclear, contradicted, not_checked
    reason: str
    current_value: Optional[str] = None
    sources: List[Source]

class CheckRequest(BaseModel):
    answer: str = Field(min_length=1, max_length=8000)

class CheckResponse(BaseModel):
    overall_freshness: Optional[int] = None
    claims: List[VerifiedClaim]
    timing_seconds: float
