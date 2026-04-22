from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.logger import get_logger
from app.models.agent_report import AgentReport
from app.models.change_event import ChangeEvent
from app.models.monitor_task import MonitorTask
from app.models.product import Product
from app.services.analyzer import analyze_changes
from app.services.collector import PlaywrightCollector
from app.services.diff_service import build_change_events
from app.services.normalizer import normalize_collected_result
from app.services.notifier import send_notification
from app.services.snapshot_service import create_snapshot, get_latest_snapshot

logger = get_logger(__name__)


def run_monitor_task(db: Session, trigger_type: str = "manual") -> dict:
    task = MonitorTask(trigger_type=trigger_type, status="running")
    db.add(task)
    db.commit()
    db.refresh(task)

    collector = PlaywrightCollector()
    snapshots_count = 0
    changes_count = 0
    reports_count = 0
    collector_errors_count = 0
    analyzer_errors_count = 0
    notifier_errors_count = 0
    successful_products_count = 0
    errors: list[str] = []

    try:
        products = db.execute(select(Product).where(Product.is_active.is_(True))).scalars().all()

        for product in products:
            previous = get_latest_snapshot(db, product.id)
            collected = collector.collect(product.product_url, product.id)
            if not collected["ok"]:
                collector_errors_count += 1
                errors.append(f"{product.product_name}: {collected['error']}")
                continue

            normalized = normalize_collected_result(collected["data"])
            normalized["product_url"] = product.product_url
            normalized["title"] = normalized["product_name"]

            current = create_snapshot(db, task.id, product.id, normalized)
            successful_products_count += 1
            snapshots_count += 1
            events = build_change_events(previous, current)
            product_events: list[dict] = []
            for event in events:
                product_events.append(event)
                db.add(
                    ChangeEvent(
                        task_id=task.id,
                        product_id=product.id,
                        event_type=event["event_type"],
                        old_value=event["old_value"],
                        new_value=event["new_value"],
                        change_ratio=event["change_ratio"],
                    )
                )
                changes_count += 1

            if product_events:
                try:
                    report = analyze_changes(product.product_name, product_events)
                except Exception as exc:  # noqa: BLE001
                    analyzer_errors_count += 1
                    errors.append(f"{product.product_name}: analyzer failed: {exc}")
                    continue
                db.add(
                    AgentReport(
                        task_id=task.id,
                        product_id=product.id,
                        summary=report["summary"],
                        priority=report["priority"],
                        suggested_action=report["suggested_action"],
                        raw_response=str(report),
                    )
                )
                reports_count += 1
                notify_result = send_notification(product.product_name, product_events, report)
                if notify_result.get("mode") == "webhook_failed":
                    notifier_errors_count += 1
                    errors.append(
                        f"{product.product_name}: notifier failed: {notify_result.get('error', 'unknown error')}"
                    )

        task.status = "succeeded" if not errors else "partial_failed"
        task.error_message = "\n".join(errors) if errors else None
    except Exception as exc:  # noqa: BLE001
        logger.exception("Task failed")
        task.status = "failed"
        task.error_message = str(exc)
    finally:
        task.finished_at = datetime.utcnow()
        db.commit()
        db.refresh(task)

    return {
        "task_id": task.id,
        "status": task.status,
        "snapshots_count": snapshots_count,
        "changes_count": changes_count,
        "reports_count": reports_count,
        "collector_errors_count": collector_errors_count,
        "analyzer_errors_count": analyzer_errors_count,
        "notifier_errors_count": notifier_errors_count,
        "successful_products_count": successful_products_count,
        "error_message": task.error_message,
    }
