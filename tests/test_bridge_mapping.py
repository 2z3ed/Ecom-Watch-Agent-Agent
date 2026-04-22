from scripts.run_multi_source_bridge_demo import _to_unified_records


def test_bridge_mapping_static_scrapy() -> None:
    summary = {
        "source_type": "static_scrapy",
        "preview_items": [{"product_name": "A", "product_url": "u", "price": 1.0, "stock_status": "in_stock", "promotion_text": ""}],
    }
    mapped = _to_unified_records(summary)
    assert mapped[0]["source_type"] == "static_scrapy"
    assert mapped[0]["price"] == 1.0


def test_bridge_mapping_discovery_candidate() -> None:
    summary = {"source_type": "discovery", "preview_items": [{"title": "T", "url": "https://x"}]}
    mapped = _to_unified_records(summary)
    assert mapped[0]["source_type"] == "discovery_candidate"
    assert mapped[0]["price"] is None
