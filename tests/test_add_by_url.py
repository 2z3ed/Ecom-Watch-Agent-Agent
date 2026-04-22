from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

from app.core.db import Base
from app.models.snapshot import Snapshot
from app.services.monitor_target_service import MonitorTargetService


def test_add_by_url_creates_target_and_baseline_snapshot(monkeypatch) -> None:
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(bind=engine)
    local_session = sessionmaker(bind=engine, autoflush=False, autocommit=False, class_=Session)

    from app.services import scrapy_adapter

    def fake_collect(self, source: str = "fixture", url: str | None = None) -> dict:
        return {
            "ok": True,
            "error": None,
            "data": {
                "product_name": "Demo URL Product",
                "product_url": url,
                "price": 88.0,
                "stock_status": "in_stock",
                "promotion_text": "none",
                "screenshot_path": None,
            },
        }

    monkeypatch.setattr(scrapy_adapter.ScrapyAdapter, "collect", fake_collect)

    service = MonitorTargetService()
    with local_session() as db:
        out = service.add_by_url(
            db=db,
            url="https://example.com/p/100",
            source_type="static_scrapy",
            product_name_hint="Hint",
        )
        assert out["product_id"] > 0
        assert out["baseline"]["status"] == "succeeded"
        assert out["baseline"]["snapshot_id"] is not None

        snapshots = db.execute(select(Snapshot)).scalars().all()
        assert len(snapshots) == 1
        assert str(snapshots[0].page_url).startswith("https://example.com")


def test_add_by_url_rejects_invalid_url() -> None:
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(bind=engine)
    local_session = sessionmaker(bind=engine, autoflush=False, autocommit=False, class_=Session)

    service = MonitorTargetService()
    with local_session() as db:
        try:
            service.add_by_url(db=db, url="not-a-url")
            assert False, "should raise ValueError for invalid url"
        except ValueError as exc:
            assert "invalid url" in str(exc)
