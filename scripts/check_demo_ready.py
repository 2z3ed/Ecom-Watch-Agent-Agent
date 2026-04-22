from pathlib import Path
import os
import sys

import httpx
from playwright.sync_api import sync_playwright
from sqlalchemy import func, select

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.core.config import settings
from app.core.db import SessionLocal
from app.models.product import Product


def check_database_exists() -> tuple[bool, str]:
    db_path = PROJECT_ROOT / "data" / "app.db"
    return db_path.exists(), f"app.db exists: {db_path}"


def check_products_seeded() -> tuple[bool, str]:
    db = SessionLocal()
    try:
        count = db.execute(select(func.count(Product.id))).scalar_one()
        return count > 0, f"products seeded count: {count}"
    finally:
        db.close()


def check_mock_state_file() -> tuple[bool, str]:
    exists = settings.mock_state_path.exists()
    state = settings.mock_state_path.read_text(encoding="utf-8").strip() if exists else "missing"
    return exists, f"mock state file: {settings.mock_state_path} ({state})"


def check_screenshots_writable() -> tuple[bool, str]:
    settings.screenshots_path.mkdir(parents=True, exist_ok=True)
    test_file = settings.screenshots_path / ".write_test"
    try:
        test_file.write_text("ok", encoding="utf-8")
        test_file.unlink(missing_ok=True)
        return True, f"screenshots dir writable: {settings.screenshots_path}"
    except Exception as exc:  # noqa: BLE001
        return False, f"screenshots dir not writable: {exc}"


def check_playwright_launchable() -> tuple[bool, str]:
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.set_content("<html><body>ok</body></html>")
            browser.close()
        return True, "playwright chromium launchable"
    except Exception as exc:  # noqa: BLE001
        return False, f"playwright launch failed: {exc}"


def check_health_endpoint() -> tuple[bool, str]:
    url = f"http://{settings.app_host}:{settings.app_port}/health"
    try:
        resp = httpx.get(url, timeout=2.0)
        return resp.status_code == 200, f"/health status: {resp.status_code}"
    except Exception as exc:  # noqa: BLE001
        return False, f"/health unreachable: {exc}"


def main() -> None:
    checks = [
        ("database", check_database_exists),
        ("products", check_products_seeded),
        ("mock_state", check_mock_state_file),
        ("screenshots", check_screenshots_writable),
        ("playwright", check_playwright_launchable),
        ("health", check_health_endpoint),
    ]

    ok_count = 0
    print("=== Demo Ready Check ===")
    for name, checker in checks:
        ok, detail = checker()
        status = "OK" if ok else "FAIL"
        if ok:
            ok_count += 1
        print(f"[{status}] {name}: {detail}")

    print(f"\nResult: {ok_count}/{len(checks)} checks passed")
    if ok_count != len(checks):
        sys.exit(1)


if __name__ == "__main__":
    os.environ.setdefault("PYTHONUNBUFFERED", "1")
    main()
