from pathlib import Path
import sys

from sqlalchemy import select

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.core.db import SessionLocal
from app.models.change_event import ChangeEvent
from app.models.monitor_task import MonitorTask
from app.models.snapshot import Snapshot
from app.models.agent_report import AgentReport
from app.services.monitor_runner import run_monitor_task


def main() -> None:
    db = SessionLocal()
    try:
        result = run_monitor_task(db, trigger_type="manual")
        print("=== TASK RESULT ===")
        print(result)

        task_id = result["task_id"]
        snapshots = db.execute(select(Snapshot).where(Snapshot.task_id == task_id)).scalars().all()
        events = db.execute(select(ChangeEvent).where(ChangeEvent.task_id == task_id)).scalars().all()
        reports = db.execute(select(AgentReport).where(AgentReport.task_id == task_id)).scalars().all()
        task = db.execute(select(MonitorTask).where(MonitorTask.id == task_id)).scalar_one()

        print("\n=== SNAPSHOTS ===")
        for snap in snapshots:
            print(
                {
                    "product_id": snap.product_id,
                    "title": snap.title,
                    "price": str(snap.price),
                    "stock_status": snap.stock_status,
                    "promotion_text": snap.promotion_text,
                    "screenshot_path": snap.screenshot_path,
                }
            )

        print("\n=== CHANGE EVENTS ===")
        if not events:
            print("No change events detected.")
        for event in events:
            print(
                {
                    "product_id": event.product_id,
                    "event_type": event.event_type,
                    "old_value": event.old_value,
                    "new_value": event.new_value,
                    "change_ratio": event.change_ratio,
                }
            )

        print("\n=== AGENT REPORTS ===")
        if not reports:
            print("No reports generated.")
        for report in reports:
            print(
                {
                    "product_id": report.product_id,
                    "summary": report.summary,
                    "priority": report.priority,
                    "suggested_action": report.suggested_action,
                }
            )

        if task.error_message:
            print("\n=== ERRORS ===")
            print(task.error_message)
    finally:
        db.close()


if __name__ == "__main__":
    main()
