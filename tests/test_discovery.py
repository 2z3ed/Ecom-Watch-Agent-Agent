from app.services.discovery import DiscoveryService


def test_discovery_dedupe_and_domain_filter() -> None:
    service = DiscoveryService()
    rows = [
        {"title": "A", "url": "https://example.com/p/1", "content": "x"},
        {"title": "A-dup", "url": "https://example.com/p/1", "content": "x"},
        {"title": "B", "url": "https://demo.com/p/2", "content": "y"},
    ]
    out = service._dedupe_and_filter(rows, ["example.com"])
    assert len(out) == 1
    assert out[0].url == "https://example.com/p/1"
