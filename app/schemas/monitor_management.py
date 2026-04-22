from datetime import datetime

from pydantic import BaseModel, Field


class MonitorTargetRow(BaseModel):
    product_id: int
    product_name: str
    product_url: str
    source_type: str
    is_active: bool
    created_at: datetime
    updated_at: datetime


class MonitorTargetsListResponse(BaseModel):
    count: int
    targets: list[MonitorTargetRow]


class MonitorTargetActionResponse(BaseModel):
    product_id: int
    status: str = Field(pattern="^(paused|resumed|deleted)$")
    is_active: bool
