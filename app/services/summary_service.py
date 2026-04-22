from datetime import datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.agent_report import AgentReport
from app.models.change_event import ChangeEvent
from app.models.product import Product


def _utc_day_range_naive(now: datetime | None = None) -> tuple[datetime, datetime, str]:
    # 当前项目大量使用 datetime.utcnow()（naive UTC）。为保证对齐，内部查询也用 naive UTC 边界。
    now = now or datetime.utcnow()
    day = now.date()
    start = datetime(day.year, day.month, day.day)
    end = start + timedelta(days=1)
    return start, end, day.isoformat()


class SummaryService:
    def get_today_summary(self, db: Session, top_limit: int = 5) -> dict:
        start, end, date_str = _utc_day_range_naive()

        total_monitored_products = db.execute(
            select(func.count(Product.id)).where(Product.is_active.is_(True))
        ).scalar_one()

        changed_products_count = db.execute(
            select(func.count(func.distinct(ChangeEvent.product_id))).where(
                ChangeEvent.detected_at >= start, ChangeEvent.detected_at < end
            )
        ).scalar_one()

        high_priority_count = db.execute(
            select(func.count(func.distinct(AgentReport.product_id))).where(
                AgentReport.created_at >= start,
                AgentReport.created_at < end,
                AgentReport.priority == "high",
            )
        ).scalar_one()

        # 取今日最新的若干条报告作为 top_items（老板视角：优先看“最新变化+建议”）。
        rows = (
            db.execute(
                select(AgentReport, Product)
                .join(Product, Product.id == AgentReport.product_id)
                .where(AgentReport.created_at >= start, AgentReport.created_at < end)
                .order_by(AgentReport.created_at.desc(), AgentReport.id.desc())
                .limit(top_limit)
            )
            .all()
        )

        top_items: list[dict] = []
        suggested_actions: list[str] = []
        seen_actions: set[str] = set()
        for report, product in rows:
            top_items.append(
                {
                    "product_id": product.id,
                    "product_name": product.product_name,
                    "summary": report.summary,
                    "priority": report.priority,
                    "suggested_action": report.suggested_action,
                }
            )
            action = (report.suggested_action or "").strip()
            if action and action not in seen_actions:
                seen_actions.add(action)
                suggested_actions.append(action)

        return {
            "date": date_str,
            "total_monitored_products": int(total_monitored_products or 0),
            "changed_products_count": int(changed_products_count or 0),
            "high_priority_count": int(high_priority_count or 0),
            "top_items": top_items,
            "suggested_actions": suggested_actions,
        }
