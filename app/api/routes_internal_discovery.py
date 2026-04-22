from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.api.internal_response import internal_success
from app.schemas.discovery_internal import DiscoveryBatchResponse, DiscoverySearchRequest
from app.schemas.internal_envelope import InternalResponse
from app.services.discovery_business_service import DiscoveryBusinessService

router = APIRouter(prefix="/internal/discovery", tags=["internal-discovery"])
service = DiscoveryBusinessService()


@router.post("/search", response_model=InternalResponse[DiscoveryBatchResponse])
def search_discovery(payload: DiscoverySearchRequest, db: Session = Depends(get_db)) -> dict:
    result = service.search_and_store(
        db=db,
        query=payload.query,
        limit=payload.limit,
        allowed_domains=payload.allowed_domains,
    )
    if not result["ok"]:
        raise HTTPException(status_code=400, detail=result["error"])
    data = DiscoveryBatchResponse(
        **{k: v for k, v in result.items() if k not in {"ok", "error", "is_fallback"}}
    )
    return internal_success(data)


@router.get("/batches/{batch_id}", response_model=InternalResponse[DiscoveryBatchResponse])
def get_discovery_batch(batch_id: int, db: Session = Depends(get_db)) -> dict:
    result = service.get_batch(db=db, batch_id=batch_id)
    if not result:
        raise HTTPException(status_code=404, detail="candidate batch not found")
    data = DiscoveryBatchResponse(**result)
    return internal_success(data)
