from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class TaskRunResponse(BaseModel):
    task_id: int
    status: str


class TaskSummary(BaseModel):
    id: int
    trigger_type: str
    status: str
    started_at: datetime
    finished_at: Optional[datetime]
    error_message: Optional[str]
