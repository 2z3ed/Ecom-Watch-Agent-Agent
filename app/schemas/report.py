from datetime import datetime

from pydantic import BaseModel


class AgentReportOut(BaseModel):
    id: int
    task_id: int
    product_id: int
    summary: str
    priority: str
    suggested_action: str
    raw_response: str
    created_at: datetime
