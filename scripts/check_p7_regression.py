from pathlib import Path
import signal
import subprocess
import sys
import time

import httpx

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def run_cmd(label: str, command: str) -> tuple[bool, str]:
    proc = subprocess.run(
        command,
        shell=True,
        cwd=PROJECT_ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    output = (proc.stdout or "").strip()
    if len(output) > 800:
        output = output[-800:]
    ok = proc.returncode == 0
    return ok, f"{label} rc={proc.returncode} output={output}"


def check_internal_apis(base: str) -> tuple[bool, str]:
    try:
        with httpx.Client(timeout=5.0, headers={"X-Request-Id": "p7-regression"}) as client:
            endpoints = [
                ("GET /internal/summary/today", "GET", f"{base}/internal/summary/today"),
                ("GET /internal/reports/latest", "GET", f"{base}/internal/reports/latest"),
                ("GET /internal/monitor/targets", "GET", f"{base}/internal/monitor/targets"),
            ]
            for name, method, url in endpoints:
                resp = client.request(method, url)
                if resp.status_code != 200:
                    return False, f"{name} status={resp.status_code}"
                payload = resp.json()
                if payload.get("ok") is not True:
                    return False, f"{name} ok=false payload={payload}"
    except Exception as exc:  # noqa: BLE001
        return False, f"internal api check failed: {exc}"
    return True, "internal apis ok"


def main() -> None:
    checks: list[tuple[bool, str]] = []

    # 1) 主链路 demo（不启动服务）
    checks.append(run_cmd("run_demo_flow", ". .venv/bin/activate && python scripts/run_demo_flow.py --reset-db"))

    # 2) 启动服务（8005）
    uvicorn_proc = subprocess.Popen(
        ". .venv/bin/activate && uvicorn app.main:app --host 127.0.0.1 --port 8005",
        shell=True,
        cwd=PROJECT_ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    time.sleep(2)

    # 3) 现有 smoke
    checks.append(run_cmd("smoke_api", ". .venv/bin/activate && python scripts/smoke_api.py"))

    # 4) P7 boss flow demo（不接飞书入口）
    checks.append(
        run_cmd(
            "p7_boss_flow_demo",
            ". .venv/bin/activate && python scripts/run_p7_boss_flow_demo.py --use-add-from-candidates",
        )
    )

    # 5) internal APIs basic availability
    ok, detail = check_internal_apis("http://127.0.0.1:8005")
    checks.append((ok, f"internal_apis: {detail}"))

    # 6) 飞书静态卡片入口（至少 dry-run 可用）
    checks.append(
        run_cmd(
            "feishu_static_card_entry",
            ". .venv/bin/activate && FEISHU_ENABLE_SEND=false python scripts/send_demo_static_card.py --target chat",
        )
    )

    try:
        uvicorn_proc.send_signal(signal.SIGTERM)
        uvicorn_proc.wait(timeout=5)
    except Exception:  # noqa: BLE001
        uvicorn_proc.kill()

    print("=== P7 Regression Check ===")
    passed = 0
    for ok, detail in checks:
        print(f"[{'OK' if ok else 'FAIL'}] {detail}")
        if ok:
            passed += 1
    print(f"\nResult: {passed}/{len(checks)} checks passed")
    if passed != len(checks):
        sys.exit(1)


if __name__ == "__main__":
    main()

