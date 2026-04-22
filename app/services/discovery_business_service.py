from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.candidate_batch import CandidateBatch
from app.models.candidate_item import CandidateItem
from app.services.discovery import DiscoveryService


class DiscoveryBusinessService:
    def __init__(self) -> None:
        self.discovery_service = DiscoveryService()

    def search_and_store(
        self,
        db: Session,
        query: str,
        limit: int | None = None,
        allowed_domains: list[str] | None = None,
    ) -> dict:
        result = self.discovery_service.search(query=query, limit=limit, allowed_domains=allowed_domains)
        if not result["ok"]:
            return {
                "ok": False,
                "error": result["error"],
            }

        batch = CandidateBatch(query=query.strip(), source_type="discovery")
        db.add(batch)
        db.flush()

        candidates: list[dict] = []
        for item in result["results"]:
            candidate = CandidateItem(
                batch_id=batch.id,
                candidate_rank=int(item["rank"]),
                title=str(item.get("title", "")).strip(),
                url=str(item.get("url", "")).strip(),
                domain=str(item.get("domain", "")).strip(),
                snippet=str(item.get("snippet", "")).strip(),
                is_selected=False,
            )
            db.add(candidate)
            db.flush()
            candidates.append(
                {
                    "candidate_id": candidate.id,
                    "candidate_rank": candidate.candidate_rank,
                    "title": candidate.title,
                    "url": candidate.url,
                    "domain": candidate.domain,
                    "snippet": candidate.snippet,
                }
            )

        db.commit()

        db.refresh(batch)
        return {
            "ok": True,
            "error": result.get("error"),
            "batch_id": batch.id,
            "query": batch.query,
            "source_type": batch.source_type,
            "created_at": batch.created_at,
            "count": len(candidates),
            "candidates": candidates,
            "is_fallback": result.get("is_fallback", False),
        }

    def get_batch(self, db: Session, batch_id: int) -> dict | None:
        batch = db.execute(select(CandidateBatch).where(CandidateBatch.id == batch_id)).scalar_one_or_none()
        if not batch:
            return None

        items = (
            db.execute(
                select(CandidateItem)
                .where(CandidateItem.batch_id == batch_id)
                .order_by(CandidateItem.candidate_rank.asc())
            )
            .scalars()
            .all()
        )
        return {
            "batch_id": batch.id,
            "query": batch.query,
            "source_type": batch.source_type,
            "created_at": batch.created_at,
            "count": len(items),
            "candidates": [
                {
                    "candidate_id": item.id,
                    "candidate_rank": item.candidate_rank,
                    "title": item.title,
                    "url": item.url,
                    "domain": item.domain,
                    "snippet": item.snippet,
                }
                for item in items
            ],
        }
