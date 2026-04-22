from datetime import datetime

from pydantic import BaseModel, Field


class DiscoverySearchRequest(BaseModel):
    query: str = Field(min_length=1, max_length=255)
    limit: int | None = Field(default=None, ge=1, le=50)
    allowed_domains: list[str] | None = None


class CandidateOut(BaseModel):
    candidate_id: int
    candidate_rank: int
    title: str
    url: str
    domain: str
    snippet: str


class DiscoveryBatchResponse(BaseModel):
    batch_id: int
    query: str
    source_type: str
    created_at: datetime
    count: int
    candidates: list[CandidateOut]
