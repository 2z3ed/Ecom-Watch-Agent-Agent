import argparse
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.services.scrape_dispatcher import ScrapeDispatcher


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run minimal multi-source dispatch demo")
    parser.add_argument(
        "--source",
        choices=["mock_playwright", "discovery", "static_scrapy", "all"],
        default="mock_playwright",
    )
    parser.add_argument("--query", default="wireless headphone")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--allowed-domains", nargs="*", default=None)
    parser.add_argument("--mode", choices=["fixture", "real"], default="fixture")
    parser.add_argument("--url", default="")
    parser.add_argument("--product-url", default="mock://product-phone")
    return parser.parse_args()


def print_summary(summary: dict) -> None:
    print(
        {
            "source_type": summary["source_type"],
            "source_mode": summary["source_mode"],
            "records_count": summary["records_count"],
            "preview_items": summary["preview_items"],
            "error": summary.get("error"),
        }
    )


def run_one(dispatcher: ScrapeDispatcher, args: argparse.Namespace, source: str) -> dict:
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

    print("=== Multi Source Demo ===")
    for source in sources:
        print(f"\n[{source}]")
        summary = run_one(dispatcher, args, source)
        print_summary(summary)


if __name__ == "__main__":
    main()
