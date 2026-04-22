from decimal import Decimal
from types import SimpleNamespace

from app.services.diff_service import build_change_events


def test_diff_service_detects_three_change_types() -> None:
    previous = SimpleNamespace(price=Decimal("100.00"), stock_status="in_stock", promotion_text="")
    current = SimpleNamespace(
        price=Decimal("80.00"), stock_status="out_of_stock", promotion_text="Flash Sale"
    )

    events = build_change_events(previous, current)
    event_types = {item["event_type"] for item in events}

    assert event_types == {"price_changed", "stock_changed", "promotion_changed"}
    price_event = [item for item in events if item["event_type"] == "price_changed"][0]
    assert price_event["change_ratio"] == -20.0


def test_diff_service_returns_empty_when_previous_none() -> None:
    current = SimpleNamespace(price=Decimal("80.00"), stock_status="in_stock", promotion_text="")
    assert build_change_events(None, current) == []
