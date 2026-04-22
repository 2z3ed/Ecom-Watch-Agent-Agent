from datetime import datetime, timezone
from decimal import Decimal

from app.services.parser import parse_price, parse_promotion, parse_stock


def normalize_collected_result(raw: dict) -> dict:
    now = datetime.now(timezone.utc)
    return {
        "product_name": raw["title"].strip(),
        "product_url": raw["page_url"].strip(),
        "price": parse_price(raw["price_text"]),
        "stock_status": parse_stock(raw["stock_text"]),
        "promotion_text": parse_promotion(raw.get("promotion_text", "")),
        "collected_at": now,
        "screenshot_path": raw["screenshot_path"],
        "title": raw["title"].strip(),
    }


def decimal_to_float(value: Decimal) -> float:
    return float(value.quantize(Decimal("0.01")))
