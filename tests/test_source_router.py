import pytest

from app.services.source_router import SourceRouter


def test_source_router_resolves_supported_types() -> None:
    router = SourceRouter()
    assert router.resolve("mock_playwright") == "mock_playwright"
    assert router.resolve("discovery") == "discovery"
    assert router.resolve("static_scrapy") == "static_scrapy"


def test_source_router_rejects_unknown_type() -> None:
    router = SourceRouter()
    with pytest.raises(ValueError, match="Unsupported source_type"):
        router.resolve("unknown_source")
