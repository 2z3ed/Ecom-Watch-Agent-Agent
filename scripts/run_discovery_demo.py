import argparse
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.services.discovery import DiscoveryService


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run minimal discovery demo with SearXNG")
    parser.add_argument("--query", required=True, help="Search query")
    parser.add_argument("--limit", type=int, default=None, help="Max number of URLs")
    parser.add_argument("--allowed-domains", nargs="*", default=None, help="Optional domain filter list")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    service = DiscoveryService()
    result = service.search(query=args.query, limit=args.limit, allowed_domains=args.allowed_domains)

    if not result["ok"]:
        print(f"[ERROR] {result['error']}")
        return

    if result.get("error"):
        print(f"[INFO] {result['error']}")
    if result.get("is_fallback"):
        print("[INFO] Discovery is running in fallback mode.")

    rows = result["results"]
    if not rows:
        print("[INFO] No discovery results found.")
        return

    print(f"Discovery results: {len(rows)}")
    for item in rows:
        print(
            {
                "rank": item["rank"],
                "title": item["title"],
                "url": item["url"],
                "domain": item["domain"],
            }
        )


if __name__ == "__main__":
    main()
