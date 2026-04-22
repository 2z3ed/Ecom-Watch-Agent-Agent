from decimal import Decimal, InvalidOperation


def parse_price(price_text: str) -> Decimal:
    cleaned = "".join(ch for ch in price_text if ch.isdigit() or ch == ".")
    if not cleaned:
        raise ValueError(f"Unable to parse price from: {price_text}")
    try:
        return Decimal(cleaned).quantize(Decimal("0.01"))
    except InvalidOperation as exc:
        raise ValueError(f"Invalid price format: {price_text}") from exc


def parse_stock(stock_text: str) -> str:
    lowered = stock_text.strip().lower()
    if lowered in {"in_stock", "in stock", "available"}:
        return "in_stock"
    if lowered in {"out_of_stock", "out of stock", "sold out"}:
        return "out_of_stock"
    return lowered or "unknown"


def parse_promotion(promotion_text: str) -> str:
    return promotion_text.strip()
