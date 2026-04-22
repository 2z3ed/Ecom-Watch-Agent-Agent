from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ChangeEventOut(BaseModel):
    id: int
    task_id: int
    product_id: int
    event_type: str
    old_value: str
    new_value: str
    change_ratio: Optional[float]
    detected_at: datetime
