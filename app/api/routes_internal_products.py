from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.internal_response import internal_success
from app.core.db import get_db
from app.schemas.boss_query import ProductDetailResponse
from app.schemas.internal_envelope import InternalResponse
from app.services.product_detail_service import ProductDetailService

router = APIRouter(prefix="/internal/products", tags=["internal-products"])
service = ProductDetailService()


@router.get("/{product_id}/detail", response_model=InternalResponse[ProductDetailResponse])
def product_detail(product_id: int, db: Session = Depends(get_db)) -> dict:
    result = service.get_product_detail(db=db, product_id=product_id)
    if not result:
        raise HTTPException(status_code=404, detail="product not found")
    data = ProductDetailResponse(**result)
    return internal_success(data)
