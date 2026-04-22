from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.product import Product


class MonitorManagementService:
    """
    P7 监控对象管理（最小版）。

    当前项目复用 `products` 表承接“正式监控对象（monitor targets）”语义：
    - is_active=true  : 参与后续监控任务
    - is_active=false : 暂停/停用（保留历史快照与报告留痕）
    """

    def list_targets(self, db: Session, include_inactive: bool = True) -> dict:
        stmt = select(Product).order_by(Product.id.asc())
        if not include_inactive:
            stmt = stmt.where(Product.is_active.is_(True))

        products = db.execute(stmt).scalars().all()
        return {
            "count": len(products),
            "targets": [
                {
                    "product_id": p.id,
                    "product_name": p.product_name,
                    "product_url": p.product_url,
                    "source_type": p.source_site,
                    "is_active": bool(p.is_active),
                    "created_at": p.created_at,
                    "updated_at": p.updated_at,
                }
                for p in products
            ],
        }

    def pause(self, db: Session, product_id: int) -> dict:
        product = db.execute(select(Product).where(Product.id == product_id)).scalar_one_or_none()
        if not product:
            raise ValueError("product not found")
        product.is_active = False
        db.commit()
        db.refresh(product)
        return {
            "product_id": product.id,
            "status": "paused",
            "is_active": bool(product.is_active),
        }

    def resume(self, db: Session, product_id: int) -> dict:
        product = db.execute(select(Product).where(Product.id == product_id)).scalar_one_or_none()
        if not product:
            raise ValueError("product not found")
        product.is_active = True
        db.commit()
        db.refresh(product)
        return {
            "product_id": product.id,
            "status": "resumed",
            "is_active": bool(product.is_active),
        }

    def delete(self, db: Session, product_id: int) -> dict:
        """
        最小删除：软删除/停用（不做硬删），以保留 snapshots/change_events/agent_reports 留痕。
        """
        product = db.execute(select(Product).where(Product.id == product_id)).scalar_one_or_none()
        if not product:
            raise ValueError("product not found")
        product.is_active = False
        db.commit()
        db.refresh(product)
        return {
            "product_id": product.id,
            "status": "deleted",
            "is_active": bool(product.is_active),
        }
