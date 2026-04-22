from datetime import datetime

from pydantic import BaseModel


class TopItemOut(BaseModel):
    product_id: int
    product_name: str
    summary: str
    priority: str
    suggested_action: str


class TodaySummaryResponse(BaseModel):
    date: str
    total_monitored_products: int
    changed_products_count: int
    high_priority_count: int
    top_items: list[TopItemOut]
    suggested_actions: list[str]


class SnapshotOut(BaseModel):
    title: str
    price: float
    stock_status: str
    promotion_text: str
    collected_at: datetime


class ChangeEventOut(BaseModel):
    event_type: str
    old_value: str
    new_value: str
    change_ratio: float | None
    detected_at: datetime


class LatestReportOut(BaseModel):
    summary: str
    priority: str
    suggested_action: str
    created_at: datetime


class ProductDetailResponse(BaseModel):
    product_id: int
    product_name: str
    product_url: str
    current_snapshot: SnapshotOut | None
    recent_change_events: list[ChangeEventOut]
    latest_report: LatestReportOut | None
    detail_summary: str


class ReportsLatestResponse(BaseModel):
    count: int
    report: TopItemOut | None
