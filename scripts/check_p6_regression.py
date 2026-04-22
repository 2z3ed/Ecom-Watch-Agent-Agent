from pathlib import Path
import signal
import subprocess
import sys
import time

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
    if len(output) > 600:
        output = output[-600:]
    ok = proc.returncode == 0
    return ok, f"{label} rc={proc.returncode} output={output}"


def main() -> None:
    checks = []
    checks.append(run_cmd("run_demo_flow", ". .venv/bin/activate && python scripts/run_demo_flow.py --reset-db"))

    uvicorn_proc = subprocess.Popen(
        ". .venv/bin/activate && uvicorn app.main:app --host 127.0.0.1 --port 8005",
        shell=True,
        cwd=PROJECT_ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    time.sleep(2)
    checks.append(run_cmd("smoke_api", ". .venv/bin/activate && python scripts/smoke_api.py"))
    try:
        uvicorn_proc.send_signal(signal.SIGTERM)
        uvicorn_proc.wait(timeout=5)
    except Exception:  # noqa: BLE001
        uvicorn_proc.kill()
    checks.append(
        run_cmd(
            "feishu_static_card_entry",
            ". .venv/bin/activate && FEISHU_ENABLE_SEND=false python scripts/send_demo_static_card.py --target chat",
        )
    )

    print("=== P6 Regression Check ===")
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
