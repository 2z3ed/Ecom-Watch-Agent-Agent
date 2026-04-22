import argparse
from datetime import datetime, timezone
from pathlib import Path
import sys
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.services.scrape_dispatcher import ScrapeDispatcher


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Bridge demo: dispatcher summary -> unified collection-like structure")
    parser.add_argument(
        "--source",
        choices=["mock_playwright", "discovery", "static_scrapy", "all"],
        default="all",
    )
    parser.add_argument("--query", default="wireless headphone")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--allowed-domains", nargs="*", default=None)
    parser.add_argument("--mode", choices=["fixture", "real"], default="fixture")
    parser.add_argument("--url", default="")
    parser.add_argument("--product-url", default="mock://product-phone")
    return parser.parse_args()


def _to_unified_records(summary: dict[str, Any]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    now = datetime.now(timezone.utc).isoformat()
    source_type = summary["source_type"]
    for item in summary.get("preview_items", []):
        if source_type == "discovery":
            records.append(
                {
                    "product_name": item.get("title", ""),
                    "product_url": item.get("url", ""),
                    "price": None,
                    "stock_status": None,
                    "promotion_text": None,
                    "collected_at": now,
                    "screenshot_path": None,
                    "source_type": "discovery_candidate",
                }
            )
        else:
            records.append(
                {
                    "product_name": item.get("product_name", ""),
                    "product_url": item.get("product_url", ""),
                    "price": item.get("price"),
                    "stock_status": item.get("stock_status"),
                    "promotion_text": item.get("promotion_text"),
                    "collected_at": now,
                    "screenshot_path": None,
                    "source_type": source_type,
                }
            )
    return records


def run_one(dispatcher: ScrapeDispatcher, args: argparse.Namespace, source: str) -> dict[str, Any]:
    if source == "mock_playwright":
        return dispatcher.dispatch("mock_playwright", product_url=args.product_url, product_id=0)
    if source == "discovery":
        return dispatcher.dispatch(
            "discovery",
            query=args.query,
            limit=args.limit,
            allowed_domains=args.allowed_domains,
        )
    if source == "static_scrapy":
        return dispatcher.dispatch("static_scrapy", mode=args.mode, url=args.url or None)
    raise ValueError(f"Unsupported source: {source}")


def main() -> None:
    args = parse_args()
    dispatcher = ScrapeDispatcher()
    sources = ["mock_playwright", "discovery", "static_scrapy"] if args.source == "all" else [args.source]

    print("=== Multi Source Bridge Demo ===")
    for source in sources:
        print(f"\n[{source}] raw summary")
        summary = run_one(dispatcher, args, source)
        print(summary)

        print(f"[{source}] mapped unified records")
        mapped = _to_unified_records(summary)
        print({"records_count": len(mapped), "records": mapped})


if __name__ == "__main__":
    main()
