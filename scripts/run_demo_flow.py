import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
import sys

from sqlalchemy import delete, select

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.core.config import settings
from app.core.db import SessionLocal
from app.models.agent_report import AgentReport
from app.models.change_event import ChangeEvent
from app.models.monitor_task import MonitorTask
from app.models.product import Product
from app.models.snapshot import Snapshot
from app.services.monitor_runner import run_monitor_task

DEFAULT_PRODUCTS = [
    {"product_name": "Mock Phone X", "product_url": "mock://product-phone", "source_site": "mock"},
    {"product_name": "Mock Headphone Pro", "product_url": "mock://product-headphone", "source_site": "mock"},
    {"product_name": "Mock Keyboard Mini", "product_url": "mock://product-keyboard", "source_site": "mock"},
]


def _set_state(target_state: str) -> None:
    settings.mock_state_path.write_text(target_state, encoding="utf-8")


def _ensure_products_seeded(db) -> None:
    existing = db.execute(select(Product)).scalars().all()
    if existing:
        return
    for item in DEFAULT_PRODUCTS:
        db.add(Product(**item))
    db.commit()


def _reset_demo_data(db) -> None:
    db.execute(delete(AgentReport))
    db.execute(delete(ChangeEvent))
    db.execute(delete(Snapshot))
    db.execute(delete(MonitorTask))
    db.commit()
    _ensure_products_seeded(db)


def _run_once(db) -> dict:
    return run_monitor_task(db, trigger_type="manual")


def _print_task_summary(title: str, result: dict) -> dict:
    print(f"\n=== {title} ===")
    summary = {
        "task_id": result["task_id"],
        "snapshots_count": result["snapshots_count"],
        "changes_count": result["changes_count"],
        "reports_count": result["reports_count"],
    }
    print(summary)
    return summary


def _print_reports_summary(db, task_id: int) -> list[dict]:
    reports = db.execute(select(AgentReport).where(AgentReport.task_id == task_id)).scalars().all()
    if not reports:
        print("No reports generated in this run.")
        return []

    products = {p.id: p.product_name for p in db.execute(select(Product)).scalars().all()}
    print("\nPer-product report summary:")
    report_summaries: list[dict] = []
    for report in reports:
        item = {
            "product_name": products.get(report.product_id, f"product-{report.product_id}"),
            "summary": report.summary,
            "priority": report.priority,
            "suggested_action": report.suggested_action,
        }
        print(item)
        report_summaries.append(item)
    return report_summaries


def _write_last_run_json(baseline: dict, changed: dict, report_summaries: list[dict]) -> None:
    output_path = PROJECT_ROOT / "data" / "demo_last_run.json"
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "baseline_run": baseline,
        "changed_run": changed,
        "report_summaries": report_summaries,
    }
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nSaved latest demo summary: {output_path}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="One-click interview demo flow")
    parser.add_argument(
        "--reset-db",
        action="store_true",
        help="Reset monitor task/result data before running (products kept).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    db = SessionLocal()
    try:
        print(">>> Demo flow started")
        if args.reset_db:
            print("Step 0/4: reset demo task/result data (keep products)")
            _reset_demo_data(db)
            print("demo data reset complete")
        else:
            print("Step 0/4: skip demo data reset (history may affect baseline diff)")

        print("Step 1/4: set mock state to baseline")
        _set_state("baseline")
        print("mock state set to baseline")

        print("\nStep 2/4: baseline first run")
        first = _run_once(db)
        baseline_summary = _print_task_summary("BASELINE RUN RESULT", first)
        if args.reset_db and (first["changes_count"] != 0 or first["reports_count"] != 0):
            print("Warning: baseline is not clean. Please check whether demo data was fully reset.")
        if not args.reset_db:
            print("Note: baseline may include historical diff because reset mode is off.")

        print("\nStep 3/4: switch mock state to changed")
        _set_state("changed")
        print("mock state switched: baseline -> changed")

        print("\nStep 4/4: changed second run")
        second = _run_once(db)
        changed_summary = _print_task_summary("CHANGED RUN RESULT", second)
        report_summaries = _print_reports_summary(db, second["task_id"])
        _write_last_run_json(baseline_summary, changed_summary, report_summaries)

        print("\n>>> Demo flow completed")
    finally:
        db.close()


if __name__ == "__main__":
    main()
