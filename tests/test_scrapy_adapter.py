from app.services.scrapy_adapter import ScrapyAdapter


def test_scrapy_adapter_fixture_output_shape(monkeypatch) -> None:
    from app.services import scrapy_adapter as module

    monkeypatch.setattr(module.settings, "enable_scrapy", True)
    adapter = ScrapyAdapter()
    result = adapter.collect(source="fixture")
    assert result["ok"] is True
    data = result["data"]
    assert data["source_type"] == "static_scrapy"
    assert data["product_name"]
    assert "product_url" in data
