from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class Snapshot(Base):
    __tablename__ = "snapshots"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    task_id: Mapped[int] = mapped_column(ForeignKey("monitor_tasks.id"), index=True, nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    stock_status: Mapped[str] = mapped_column(String(50), nullable=False)
    promotion_text: Mapped[str] = mapped_column(Text, nullable=False, default="")
    page_url: Mapped[str] = mapped_column(String(1024), nullable=False)
    screenshot_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    collected_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
