from decimal import Decimal

from app.services.normalizer import normalize_collected_result


def test_normalize_collected_result_maps_fields() -> None:
    raw = {
        "title": " Mock Product ",
        "page_url": "mock://product-phone",
        "price_text": "1299.00",
        "stock_text": "in_stock",
        "promotion_text": "Member Discount",
        "screenshot_path": "data/screenshots/a.png",
    }

    normalized = normalize_collected_result(raw)
    assert normalized["product_name"] == "Mock Product"
    assert normalized["product_url"] == "mock://product-phone"
    assert normalized["price"] == Decimal("1299.00")
    assert normalized["stock_status"] == "in_stock"
    assert normalized["promotion_text"] == "Member Discount"
    assert "collected_at" in normalized
