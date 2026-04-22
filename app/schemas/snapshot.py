from datetime import datetime

from pydantic import BaseModel


class SnapshotOut(BaseModel):
    id: int
    task_id: int
    product_id: int
    title: str
    price: float
    stock_status: str
    promotion_text: str
    page_url: str
    screenshot_path: str
    collected_at: datetime
