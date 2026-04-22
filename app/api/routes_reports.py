from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models.agent_report import AgentReport

router = APIRouter(prefix="/api/v1/reports", tags=["reports"])


@router.get("/latest")
def latest_report(db: Session = Depends(get_db)) -> dict:
    report = db.execute(select(AgentReport).order_by(desc(AgentReport.id)).limit(1)).scalar_one_or_none()
    if not report:
        raise HTTPException(status_code=404, detail="no reports found")
    return {
        "id": report.id,
        "task_id": report.task_id,
        "product_id": report.product_id,
        "summary": report.summary,
        "priority": report.priority,
        "suggested_action": report.suggested_action,
        "raw_response": report.raw_response,
        "created_at": report.created_at,
    }
