from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import httpx

from app.core.config import settings

try:
    from scrapy import Selector
except Exception:  # noqa: BLE001
    Selector = None


class ScrapyAdapter:
    def __init__(self) -> None:
        self.fixture_file = settings.scrapy_fixture_path / "product_fixture.html"

    def _parse_html(self, html: str, page_url: str, source_mode: str) -> dict[str, Any]:
        if Selector is None:
            raise RuntimeError("Scrapy is not installed. Please install dependencies first.")

        selector = Selector(text=html)
        title = selector.css("[data-field='title']::text").get(default="").strip()
        price_text = selector.css("[data-field='price']::text").get(default="").strip()
        stock_text = selector.css("[data-field='stock']::text").get(default="").strip()
        promo_text = selector.css("[data-field='promotion']::text").get(default="").strip()

        if not title:
            raise ValueError("Missing required field: title")

        return {
            "product_name": title,
            "product_url": page_url,
            "price": self._parse_price(price_text),
            "stock_status": stock_text or "unknown",
            "promotion_text": promo_text,
            "collected_at": datetime.now(timezone.utc).isoformat(),
            "screenshot_path": None,
            "source_type": "static_scrapy",
            "source_mode": source_mode,
        }

    def _parse_price(self, price_text: str) -> float:
        cleaned = "".join(ch for ch in price_text if ch.isdigit() or ch == ".")
        if not cleaned:
            return 0.0
        return float(cleaned)

    def collect_from_fixture(self) -> dict[str, Any]:
        if not self.fixture_file.exists():
            raise FileNotFoundError(f"Fixture file not found: {self.fixture_file}")
        html = self.fixture_file.read_text(encoding="utf-8")
        return self._parse_html(
            html=html,
            page_url=self.fixture_file.resolve().as_uri(),
            source_mode="fixture",
        )

    def collect_from_url(self, url: str) -> dict[str, Any]:
        with httpx.Client(timeout=10.0, follow_redirects=True) as client:
            resp = client.get(url)
            resp.raise_for_status()
        return self._parse_html(html=resp.text, page_url=url, source_mode="real")

    def collect(self, source: str = "fixture", url: str | None = None) -> dict[str, Any]:
        if not settings.enable_scrapy:
            return {"ok": False, "error": "Scrapy adapter is disabled. Set ENABLE_SCRAPY=true.", "data": None}

        if source == "fixture":
            try:
                data = self.collect_from_fixture()
                return {"ok": True, "error": None, "data": data}
            except Exception as exc:  # noqa: BLE001
                return {"ok": False, "error": f"Fixture collect failed: {exc}", "data": None}

        if source == "real":
            if not url:
                return {"ok": False, "error": "URL is required when source=real.", "data": None}
            try:
                data = self.collect_from_url(url)
                return {"ok": True, "error": None, "data": data}
            except Exception as exc:  # noqa: BLE001
                try:
                    fallback = self.collect_from_fixture()
                    return {
                        "ok": True,
                        "error": f"Real source failed: {exc}. Fallback to fixture.",
                        "data": fallback,
                    }
                except Exception as fixture_exc:  # noqa: BLE001
                    return {
                        "ok": False,
                        "error": f"Real source failed: {exc}. Fixture fallback failed: {fixture_exc}",
                        "data": None,
                    }

        return {"ok": False, "error": f"Unsupported source: {source}", "data": None}
