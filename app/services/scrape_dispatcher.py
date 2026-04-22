from typing import Any

from app.services.collector import PlaywrightCollector
from app.services.discovery import DiscoveryService
from app.services.normalizer import normalize_collected_result
from app.services.scrapy_adapter import ScrapyAdapter
from app.services.source_router import SourceRouter


class ScrapeDispatcher:
    def __init__(self) -> None:
        self.router = SourceRouter()
        self.collector = PlaywrightCollector()
        self.discovery = DiscoveryService()
        self.scrapy = ScrapyAdapter()

    def dispatch(self, source_type: str, **kwargs) -> dict[str, Any]:
        resolved = self.router.resolve(source_type)
        if resolved == "mock_playwright":
            return self._dispatch_mock_playwright(**kwargs)
        if resolved == "discovery":
            return self._dispatch_discovery(**kwargs)
        if resolved == "static_scrapy":
            return self._dispatch_static_scrapy(**kwargs)
        raise ValueError(f"Unhandled source_type: {resolved}")

    def _dispatch_mock_playwright(self, **kwargs) -> dict[str, Any]:
        product_url = kwargs.get("product_url", "mock://product-phone")
        product_id = kwargs.get("product_id", 0)
        collected = self.collector.collect(product_url=product_url, product_id=product_id)
        if not collected["ok"]:
            return {
                "source_type": "mock_playwright",
                "source_mode": "mock",
                "records_count": 0,
                "preview_items": [],
                "error": collected["error"],
            }

        normalized = normalize_collected_result(collected["data"])
        item = {
            "product_name": normalized["product_name"],
            "product_url": product_url,
            "price": float(normalized["price"]),
            "stock_status": normalized["stock_status"],
            "promotion_text": normalized["promotion_text"],
        }
        return {
            "source_type": "mock_playwright",
            "source_mode": "mock" if str(product_url).startswith("mock://") else "real",
            "records_count": 1,
            "preview_items": [item],
            "error": None,
        }

    def _dispatch_discovery(self, **kwargs) -> dict[str, Any]:
        query = kwargs.get("query", "")
        limit = kwargs.get("limit")
        allowed_domains = kwargs.get("allowed_domains")
        result = self.discovery.search(query=query, limit=limit, allowed_domains=allowed_domains)
        if not result["ok"]:
            return {
                "source_type": "discovery",
                "source_mode": "error",
                "records_count": 0,
                "preview_items": [],
                "error": result["error"],
            }

        preview = [
            {"title": item["title"], "url": item["url"], "domain": item["domain"]}
            for item in result["results"][:5]
        ]
        return {
            "source_type": "discovery",
            "source_mode": "fallback" if result.get("is_fallback") else "real",
            "records_count": len(result["results"]),
            "preview_items": preview,
            "error": result.get("error"),
        }

    def _dispatch_static_scrapy(self, **kwargs) -> dict[str, Any]:
        source_mode = kwargs.get("mode", "fixture")
        url = kwargs.get("url")
        result = self.scrapy.collect(source=source_mode, url=url)
        if not result["ok"]:
            return {
                "source_type": "static_scrapy",
                "source_mode": source_mode,
                "records_count": 0,
                "preview_items": [],
                "error": result["error"],
            }

        data = result["data"]
        item = {
            "product_name": data["product_name"],
            "product_url": data["product_url"],
            "price": data["price"],
            "stock_status": data["stock_status"],
            "promotion_text": data["promotion_text"],
        }
        return {
            "source_type": "static_scrapy",
            "source_mode": data.get("source_mode", source_mode),
            "records_count": 1,
            "preview_items": [item],
            "error": result.get("error"),
        }
