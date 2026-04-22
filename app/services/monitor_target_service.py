from datetime import datetime, timezone
from urllib.parse import urlparse

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.candidate_batch import CandidateBatch
from app.models.candidate_item import CandidateItem
from app.models.monitor_task import MonitorTask
from app.models.product import Product
from app.services.snapshot_service import create_snapshot


class MonitorTargetService:
    def _infer_source_type(self, url: str, source_type: str | None) -> str:
        if source_type:
            return source_type
        if url.startswith("mock://"):
            return "mock_playwright"
        return "static_scrapy"

    def _validate_url(self, url: str) -> str:
        cleaned = url.strip()
        if cleaned.startswith("mock://"):
            return cleaned
        parsed = urlparse(cleaned)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ValueError("invalid url: only http/https/mock:// are supported")
        return cleaned

    def _get_or_create_product(
        self,
        db: Session,
        url: str,
        source_type: str,
        product_name_hint: str | None = None,
    ) -> Product:
        product = db.execute(select(Product).where(Product.product_url == url)).scalar_one_or_none()
        if product:
            product.is_active = True
            if product_name_hint and not product.product_name.strip():
                product.product_name = product_name_hint.strip()
            db.flush()
            return product

        parsed = urlparse(url if not url.startswith("mock://") else "https://mock.local/" + url.replace("mock://", "", 1))
        source_site = source_type
        name = (product_name_hint or "").strip() or parsed.path.strip("/").split("/")[-1] or parsed.netloc or "new target"
        product = Product(
            product_name=name[:255],
            product_url=url,
            source_site=source_site[:100],
            is_active=True,
        )
        db.add(product)
        db.flush()
        return product

    def _build_minimal_baseline(self, db: Session, product: Product, source_type: str) -> dict:
        task = MonitorTask(trigger_type="baseline_init", status="running")
        db.add(task)
        db.commit()
        db.refresh(task)

        snapshot_id: int | None = None
        collected_at: datetime | None = None
        error: str | None = None

        try:
            if source_type == "mock_playwright":
                # Lazy import to avoid hard dependency at module import time.
                from app.services.collector import PlaywrightCollector
                from app.services.normalizer import normalize_collected_result

                collector = PlaywrightCollector()
                collected = collector.collect(product_url=product.product_url, product_id=product.id)
                if not collected["ok"]:
                    raise RuntimeError(f"baseline collect failed: {collected['error']}")

                normalized = normalize_collected_result(collected["data"])
                normalized["product_url"] = product.product_url
                normalized["title"] = normalized["product_name"]
                snapshot = create_snapshot(db, task.id, product.id, normalized)
                snapshot_id = snapshot.id
                collected_at = snapshot.collected_at

                if product.product_name.startswith("new target") and normalized.get("product_name"):
                    product.product_name = str(normalized["product_name"])[:255]
                    db.flush()
            elif source_type == "static_scrapy":
                from app.services.scrapy_adapter import ScrapyAdapter

                adapter = ScrapyAdapter()
                collected = adapter.collect(source="real", url=product.product_url)
                if not collected["ok"] or not collected.get("data"):
                    raise RuntimeError(f"baseline collect failed: {collected.get('error', 'unknown error')}")
                data = collected["data"]
                normalized = {
                    "title": data.get("product_name", product.product_name),
                    "price": data.get("price", 0.0),
                    "stock_status": data.get("stock_status", "unknown"),
                    "promotion_text": data.get("promotion_text", ""),
                    "product_url": product.product_url,
                    "screenshot_path": data.get("screenshot_path") or "",
                    "collected_at": datetime.now(timezone.utc),
                }
                snapshot = create_snapshot(db, task.id, product.id, normalized)
                snapshot_id = snapshot.id
                collected_at = snapshot.collected_at
            else:
                raise RuntimeError(f"unsupported source_type for baseline: {source_type}")

            task.status = "succeeded"
            task.error_message = None
        except Exception as exc:  # noqa: BLE001
            task.status = "failed"
            error = str(exc)
            task.error_message = error
        finally:
            task.finished_at = datetime.utcnow()
            db.commit()
            db.refresh(task)

        return {
            "task_id": task.id,
            "status": task.status,
            "snapshot_id": snapshot_id,
            "collected_at": collected_at,
            "error": error,
        }

    def add_from_candidates(
        self,
        db: Session,
        batch_id: int,
        candidate_ids: list[int],
        source_type: str | None = None,
    ) -> list[dict]:
        batch = db.execute(select(CandidateBatch).where(CandidateBatch.id == batch_id)).scalar_one_or_none()
        if not batch:
            raise ValueError("candidate batch not found")

        items = (
            db.execute(
                select(CandidateItem)
                .where(CandidateItem.batch_id == batch_id, CandidateItem.id.in_(candidate_ids))
                .order_by(CandidateItem.candidate_rank.asc())
            )
            .scalars()
            .all()
        )
        if not items:
            raise ValueError("no candidate items found for provided candidate_ids")

        requested_ids = set(candidate_ids)
        found_ids = {item.id for item in items}
        missing = sorted(requested_ids - found_ids)
        if missing:
            raise ValueError(f"candidate_ids not found in batch {batch_id}: {missing}")

        outputs: list[dict] = []
        for item in items:
            validated_url = self._validate_url(item.url)
            target_source_type = self._infer_source_type(validated_url, source_type or batch.source_type)
            product = self._get_or_create_product(
                db=db,
                url=validated_url,
                source_type=target_source_type,
                product_name_hint=item.title,
            )
            baseline = self._build_minimal_baseline(db=db, product=product, source_type=target_source_type)
            item.is_selected = True
            db.flush()
            outputs.append(
                {
                    "product_id": product.id,
                    "product_name": product.product_name,
                    "product_url": product.product_url,
                    "source_type": target_source_type,
                    "baseline": baseline,
                }
            )
        db.commit()
        return outputs

    def add_by_url(
        self,
        db: Session,
        url: str,
        source_type: str | None = None,
        product_name_hint: str | None = None,
    ) -> dict:
        validated_url = self._validate_url(url)
        target_source_type = self._infer_source_type(validated_url, source_type)
        product = self._get_or_create_product(
            db=db,
            url=validated_url,
            source_type=target_source_type,
            product_name_hint=product_name_hint,
        )
        baseline = self._build_minimal_baseline(db=db, product=product, source_type=target_source_type)
        return {
            "product_id": product.id,
            "product_name": product.product_name,
            "product_url": product.product_url,
            "source_type": target_source_type,
            "baseline": baseline,
        }
