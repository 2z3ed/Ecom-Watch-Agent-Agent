from decimal import Decimal


def _to_text(value: object) -> str:
    return "" if value is None else str(value)


def build_change_events(previous, current) -> list[dict]:
    events: list[dict] = []

    if previous is None:
        return events

    if previous.price != current.price:
        ratio = None
        if previous.price and previous.price != Decimal("0"):
            ratio = float(((current.price - previous.price) / previous.price) * Decimal("100"))
        events.append(
            {
                "event_type": "price_changed",
                "old_value": _to_text(previous.price),
                "new_value": _to_text(current.price),
                "change_ratio": ratio,
            }
        )

    if previous.stock_status != current.stock_status:
        events.append(
            {
                "event_type": "stock_changed",
                "old_value": _to_text(previous.stock_status),
                "new_value": _to_text(current.stock_status),
                "change_ratio": None,
            }
        )

    if (previous.promotion_text or "") != (current.promotion_text or ""):
        events.append(
            {
                "event_type": "promotion_changed",
                "old_value": _to_text(previous.promotion_text),
                "new_value": _to_text(current.promotion_text),
                "change_ratio": None,
            }
        )

    return events
