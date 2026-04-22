from pathlib import Path
import json
import sys

import httpx

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.core.config import settings


def _print_result(ok: bool, name: str, detail: str) -> None:
    status = "OK" if ok else "FAIL"
    print(f"[{status}] {name}: {detail}")


def main() -> None:
    base = f"http://{settings.app_host}:{settings.app_port}"
    checks: list[tuple[str, bool, str]] = []

    try:
        with httpx.Client(timeout=5.0) as client:
            health = client.get(f"{base}/health")
            checks.append(("GET /health", health.status_code == 200, f"status={health.status_code}"))

            latest_task = client.get(f"{base}/api/v1/tasks/latest")
            task_ok = latest_task.status_code == 200
            checks.append(("GET /api/v1/tasks/latest", task_ok, f"status={latest_task.status_code}"))

            latest_task_id = None
            if task_ok:
                payload = latest_task.json()
                latest_task_id = payload.get("task_id")
                checks.append(("tasks/latest has task_id", latest_task_id is not None, f"task_id={latest_task_id}"))

            latest_report = client.get(f"{base}/api/v1/reports/latest")
            report_ok = latest_report.status_code in {200, 404}
            checks.append(
                (
                    "GET /api/v1/reports/latest",
                    report_ok,
                    f"status={latest_report.status_code} (404 means no report yet)",
                )
            )

            if latest_task_id is not None:
                detail = client.get(f"{base}/api/v1/tasks/{latest_task_id}")
                checks.append(
                    (
                        f"GET /api/v1/tasks/{latest_task_id}",
                        detail.status_code == 200,
                        f"status={detail.status_code}",
                    )
                )
            else:
                checks.append(("GET /api/v1/tasks/{task_id}", False, "skipped because task_id is missing"))
    except Exception as exc:  # noqa: BLE001
        checks.append(("API connectivity", False, str(exc)))

    demo_json_path = PROJECT_ROOT / "data" / "demo_last_run.json"
    if demo_json_path.exists():
        try:
            payload = json.loads(demo_json_path.read_text(encoding="utf-8"))
            required = {"generated_at", "baseline_run", "changed_run", "report_summaries"}
            missing = required - set(payload.keys())
            checks.append(
                (
                    "demo_last_run.json structure",
                    len(missing) == 0,
                    "ok" if not missing else f"missing fields: {sorted(missing)}",
                )
            )
        except Exception as exc:  # noqa: BLE001
            checks.append(("demo_last_run.json parse", False, str(exc)))
    else:
        checks.append(("demo_last_run.json exists", False, f"not found: {demo_json_path}"))

    print("=== API Smoke Test ===")
    passed = 0
    for name, ok, detail in checks:
        _print_result(ok, name, detail)
        if ok:
            passed += 1

    print(f"\nResult: {passed}/{len(checks)} checks passed")
    if passed != len(checks):
        sys.exit(1)


if __name__ == "__main__":
    main()
