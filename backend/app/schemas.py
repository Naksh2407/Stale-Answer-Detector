from pydantic import BaseModel, Field
from typing import List, Optional


class Source(BaseModel):
    title: str
    url: str
    published_date: Optional[str] = None


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
    answer: Optional[str] = Field(default=None, max_length=8000)
    url: Optional[str] = Field(default=None)


class CheckResponse(BaseModel):
    overall_freshness: Optional[int] = None
    summary_sentence: str
    corrected_answer: Optional[str] = None
    claims: List[VerifiedClaim]
    timing_seconds: float


class BatchRequest(BaseModel):
    answers: List[str] = Field(min_length=1, max_length=10)


class BatchResponse(BaseModel):
    results: List[dict]
    count: int


class DemoResponse(BaseModel):
    answer: str
    overall_freshness: Optional[int] = None
    summary_sentence: str
    corrected_answer: Optional[str] = None
    claims: List[VerifiedClaim]
    timing_seconds: float
