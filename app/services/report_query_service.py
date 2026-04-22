from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.models.agent_report import AgentReport
from app.models.product import Product


class ReportQueryService:
    def get_latest_report(self, db: Session) -> dict:
        row = (
            db.execute(
                select(AgentReport, Product)
                .join(Product, Product.id == AgentReport.product_id)
                .order_by(desc(AgentReport.created_at), desc(AgentReport.id))
                .limit(1)
            )
            .first()
        )
        if not row:
            return {"count": 0, "report": None}

        report, product = row
        return {
            "count": 1,
            "report": {
                "product_id": product.id,
                "product_name": product.product_name,
                "summary": report.summary,
                "priority": report.priority,
                "suggested_action": report.suggested_action,
                "created_at": report.created_at,
            },
        }
