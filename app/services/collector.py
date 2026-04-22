from datetime import datetime
from pathlib import Path

from playwright.sync_api import sync_playwright

from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger(__name__)


class PlaywrightCollector:
    def __init__(self) -> None:
        settings.screenshots_path.mkdir(parents=True, exist_ok=True)

    def _resolve_url(self, product_url: str) -> str:
        if not product_url.startswith("mock://"):
            return product_url
        slug = product_url.replace("mock://", "", 1)
        state = settings.mock_state_path.read_text(encoding="utf-8").strip()
        target_file = settings.mock_pages_path / state / f"{slug}.html"
        if not target_file.exists():
            raise FileNotFoundError(f"Mock page not found: {target_file}")
        return target_file.resolve().as_uri()

    def collect(self, product_url: str, product_id: int) -> dict:
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        screenshot_name = f"product_{product_id}_{timestamp}.png"
        screenshot_path = settings.screenshots_path / screenshot_name
        target_url = self._resolve_url(product_url)

        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.goto(target_url, wait_until="domcontentloaded", timeout=15000)
                page.wait_for_selector("[data-field='title']", timeout=5000)
                raw = {
                    "title": page.locator("[data-field='title']").inner_text().strip(),
                    "price_text": page.locator("[data-field='price']").inner_text().strip(),
                    "stock_text": page.locator("[data-field='stock']").inner_text().strip(),
                    "promotion_text": page.locator("[data-field='promotion']").inner_text().strip(),
                    "page_url": target_url,
                    "screenshot_path": str(screenshot_path),
                }
                page.screenshot(path=str(screenshot_path), full_page=True)
                browser.close()
            return {"ok": True, "data": raw}
        except Exception as exc:  # noqa: BLE001
            logger.exception("Collect failed for %s", target_url)
            return {"ok": False, "error": str(exc), "page_url": target_url}
