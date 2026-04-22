from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.db import Base
from app.models.candidate_batch import CandidateBatch
from app.models.candidate_item import CandidateItem
from app.services.monitor_target_service import MonitorTargetService


def test_add_from_candidates_creates_monitor_target(monkeypatch) -> None:
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(bind=engine)
    local_session = sessionmaker(bind=engine, autoflush=False, autocommit=False, class_=Session)

    service = MonitorTargetService()

    def fake_baseline(db, product, source_type: str) -> dict:
        return {
            "task_id": 1,
            "status": "succeeded",
            "snapshot_id": 10,
            "collected_at": None,
            "error": None,
        }

    monkeypatch.setattr(service, "_build_minimal_baseline", fake_baseline)

    with local_session() as db:
        batch = CandidateBatch(query="phone", source_type="discovery")
        db.add(batch)
        db.flush()
        item = CandidateItem(
            batch_id=batch.id,
            candidate_rank=1,
            title="Phone A",
            url="https://example.com/p/a",
            domain="example.com",
            snippet="demo",
            is_selected=False,
        )
        db.add(item)
        db.commit()

        result = service.add_from_candidates(
            db=db,
            batch_id=batch.id,
            candidate_ids=[item.id],
            source_type="static_scrapy",
        )
        assert len(result) == 1
        assert result[0]["product_id"] > 0
        assert result[0]["baseline"]["status"] == "succeeded"
        db.refresh(item)
        assert item.is_selected is True
