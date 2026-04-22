from datetime import datetime

from pydantic import BaseModel, Field


class AddFromCandidatesRequest(BaseModel):
    batch_id: int = Field(gt=0)
    candidate_ids: list[int] = Field(min_length=1)
    source_type: str | None = None


class AddByUrlRequest(BaseModel):
    url: str = Field(min_length=1, max_length=2048)
    source_type: str | None = None
    product_name_hint: str | None = Field(default=None, max_length=255)


class BaselineSummary(BaseModel):
    task_id: int
    status: str
    snapshot_id: int | None
    collected_at: datetime | None
    error: str | None


class MonitorTargetOut(BaseModel):
    product_id: int
    product_name: str
    product_url: str
    source_type: str
    baseline: BaselineSummary


class AddTargetsResponse(BaseModel):
    count: int
    targets: list[MonitorTargetOut]
