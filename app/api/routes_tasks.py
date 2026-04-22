from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models.agent_report import AgentReport
from app.models.change_event import ChangeEvent
from app.models.monitor_task import MonitorTask
from app.models.snapshot import Snapshot
from app.schemas.task import TaskRunResponse
from app.services.monitor_runner import run_monitor_task

router = APIRouter(prefix="/api/v1/tasks", tags=["tasks"])


@router.post("/run", response_model=TaskRunResponse)
def run_task(db: Session = Depends(get_db)) -> TaskRunResponse:
    result = run_monitor_task(db, trigger_type="manual")
    return TaskRunResponse(task_id=result["task_id"], status=result["status"])


@router.get("/latest")
def latest_task(db: Session = Depends(get_db)) -> dict:
    task = db.execute(select(MonitorTask).order_by(desc(MonitorTask.id)).limit(1)).scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="no tasks found")

    snapshots_count = db.execute(
        select(func.count(Snapshot.id)).where(Snapshot.task_id == task.id)
    ).scalar_one()
    changes_count = db.execute(
        select(func.count(ChangeEvent.id)).where(ChangeEvent.task_id == task.id)
    ).scalar_one()
    reports_count = db.execute(
        select(func.count(AgentReport.id)).where(AgentReport.task_id == task.id)
    ).scalar_one()

    return {
        "task_id": task.id,
        "status": task.status,
        "trigger_type": task.trigger_type,
        "started_at": task.started_at,
        "finished_at": task.finished_at,
        "snapshots_count": snapshots_count,
        "changes_count": changes_count,
        "reports_count": reports_count,
        "error_message": task.error_message,
    }


@router.get("/{task_id}")
def task_detail(task_id: int, db: Session = Depends(get_db)) -> dict:
    task = db.execute(select(MonitorTask).where(MonitorTask.id == task_id)).scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="task not found")

    snapshots = db.execute(select(Snapshot).where(Snapshot.task_id == task_id)).scalars().all()
    change_events = db.execute(select(ChangeEvent).where(ChangeEvent.task_id == task_id)).scalars().all()
    reports = db.execute(select(AgentReport).where(AgentReport.task_id == task_id)).scalars().all()

    return {
        "task": {
            "id": task.id,
            "trigger_type": task.trigger_type,
            "status": task.status,
            "started_at": task.started_at,
            "finished_at": task.finished_at,
            "error_message": task.error_message,
        },
        "snapshots": [
            {
                "id": item.id,
                "product_id": item.product_id,
                "title": item.title,
                "price": float(item.price),
                "stock_status": item.stock_status,
                "promotion_text": item.promotion_text,
                "page_url": item.page_url,
                "screenshot_path": item.screenshot_path,
                "collected_at": item.collected_at,
            }
            for item in snapshots
        ],
        "change_events": [
            {
                "id": item.id,
                "product_id": item.product_id,
                "event_type": item.event_type,
                "old_value": item.old_value,
                "new_value": item.new_value,
                "change_ratio": item.change_ratio,
                "detected_at": item.detected_at,
            }
            for item in change_events
        ],
        "agent_reports": [
            {
                "id": item.id,
                "product_id": item.product_id,
                "summary": item.summary,
                "priority": item.priority,
                "suggested_action": item.suggested_action,
                "raw_response": item.raw_response,
                "created_at": item.created_at,
            }
            for item in reports
        ],
    }
