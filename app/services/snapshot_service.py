from typing import Optional

from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.models.snapshot import Snapshot


def get_latest_snapshot(db: Session, product_id: int) -> Optional[Snapshot]:
    stmt = (
        select(Snapshot)
        .where(Snapshot.product_id == product_id)
        .order_by(desc(Snapshot.collected_at), desc(Snapshot.id))
        .limit(1)
    )
    return db.execute(stmt).scalar_one_or_none()


def create_snapshot(db: Session, task_id: int, product_id: int, normalized: dict) -> Snapshot:
    snapshot = Snapshot(
        task_id=task_id,
        product_id=product_id,
        title=normalized["title"],
        price=normalized["price"],
        stock_status=normalized["stock_status"],
        promotion_text=normalized["promotion_text"],
        page_url=normalized["product_url"],
        screenshot_path=normalized["screenshot_path"],
        collected_at=normalized["collected_at"],
    )
    db.add(snapshot)
    db.flush()
    return snapshot
