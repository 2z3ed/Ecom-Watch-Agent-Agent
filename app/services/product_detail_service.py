from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.models.agent_report import AgentReport
from app.models.change_event import ChangeEvent
from app.models.product import Product
from app.models.snapshot import Snapshot


class ProductDetailService:
    def get_product_detail(self, db: Session, product_id: int) -> dict | None:
        product = db.execute(select(Product).where(Product.id == product_id)).scalar_one_or_none()
        if not product:
            return None

        snapshot = db.execute(
            select(Snapshot)
            .where(Snapshot.product_id == product_id)
            .order_by(desc(Snapshot.collected_at), desc(Snapshot.id))
            .limit(1)
        ).scalar_one_or_none()

        change_events = (
            db.execute(
                select(ChangeEvent)
                .where(ChangeEvent.product_id == product_id)
                .order_by(desc(ChangeEvent.detected_at), desc(ChangeEvent.id))
                .limit(10)
            )
            .scalars()
            .all()
        )

        report = db.execute(
            select(AgentReport)
            .where(AgentReport.product_id == product_id)
            .order_by(desc(AgentReport.created_at), desc(AgentReport.id))
            .limit(1)
        ).scalar_one_or_none()

        if report:
            detail_summary = report.summary
        elif snapshot:
            detail_summary = f"当前价格 {snapshot.price}，库存 {snapshot.stock_status}，活动 {snapshot.promotion_text or '无'}。"
        else:
            detail_summary = "暂无采集快照与分析报告。"

        return {
            "product_id": product.id,
            "product_name": product.product_name,
            "product_url": product.product_url,
            "current_snapshot": None
            if not snapshot
            else {
                "title": snapshot.title,
                "price": float(snapshot.price),
                "stock_status": snapshot.stock_status,
                "promotion_text": snapshot.promotion_text,
                "collected_at": snapshot.collected_at,
            },
            "recent_change_events": [
                {
                    "event_type": item.event_type,
                    "old_value": item.old_value,
                    "new_value": item.new_value,
                    "change_ratio": item.change_ratio,
                    "detected_at": item.detected_at,
                }
                for item in change_events
            ],
            "latest_report": None
            if not report
            else {
                "summary": report.summary,
                "priority": report.priority,
                "suggested_action": report.suggested_action,
                "created_at": report.created_at,
            },
            "detail_summary": detail_summary,
        }
