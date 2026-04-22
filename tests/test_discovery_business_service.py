from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

from app.core.db import Base
from app.models.candidate_batch import CandidateBatch
from app.models.candidate_item import CandidateItem
from app.services.discovery_business_service import DiscoveryBusinessService


def test_search_and_store_creates_batch_and_items(monkeypatch) -> None:
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(bind=engine)
    local_session = sessionmaker(bind=engine, autoflush=False, autocommit=False, class_=Session)

    def fake_search(query: str, limit: int | None = None, allowed_domains: list[str] | None = None) -> dict:
        return {
            "ok": True,
            "error": None,
            "is_fallback": False,
            "results": [
                {"rank": 1, "title": "A", "url": "https://example.com/a", "domain": "example.com", "snippet": "s1"},
                {"rank": 2, "title": "B", "url": "https://demo.com/b", "domain": "demo.com", "snippet": "s2"},
            ],
        }

    service = DiscoveryBusinessService()
    monkeypatch.setattr(service.discovery_service, "search", fake_search)

    with local_session() as db:
        result = service.search_and_store(db=db, query="phone", limit=2, allowed_domains=None)
        assert result["ok"] is True
        assert result["count"] == 2

        batches = db.execute(select(CandidateBatch)).scalars().all()
        items = db.execute(select(CandidateItem).order_by(CandidateItem.candidate_rank)).scalars().all()
        assert len(batches) == 1
        assert len(items) == 2
        assert items[0].url == "https://example.com/a"


def test_get_batch_returns_candidates(monkeypatch) -> None:
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(bind=engine)
    local_session = sessionmaker(bind=engine, autoflush=False, autocommit=False, class_=Session)

    service = DiscoveryBusinessService()

    with local_session() as db:
        batch = CandidateBatch(query="phone", source_type="discovery")
        db.add(batch)
        db.flush()
        db.add(CandidateItem(batch_id=batch.id, candidate_rank=1, title="T", url="https://example.com/1", domain="example.com", snippet="snip"))
        db.commit()

        out = service.get_batch(db=db, batch_id=batch.id)
        assert out is not None
        assert out["batch_id"] == batch.id
        assert out["count"] == 1
        assert out["candidates"][0]["candidate_rank"] == 1
