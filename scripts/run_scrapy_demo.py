import argparse
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.core.config import settings
from app.services.scrapy_adapter import ScrapyAdapter


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run minimal Scrapy static collection demo")
    parser.add_argument("--source", choices=["fixture", "real"], default=settings.scrapy_default_source)
    parser.add_argument("--url", default="", help="Real page URL when source=real")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    adapter = ScrapyAdapter()

    source = args.source
    if args.url:
        source = "real"

    result = adapter.collect(source=source, url=args.url or None)
    if not result["ok"]:
        print(f"[ERROR] {result['error']}")
        return

    if result.get("error"):
        print(f"[INFO] {result['error']}")

    data = result["data"]
    print("Scrapy demo result:")
    print(
        {
            "product_name": data["product_name"],
            "product_url": data["product_url"],
            "price": data["price"],
            "stock_status": data["stock_status"],
            "promotion_text": data["promotion_text"],
            "source_type": data["source_type"],
            "source_mode": data["source_mode"],
        }
    )


if __name__ == "__main__":
    main()
