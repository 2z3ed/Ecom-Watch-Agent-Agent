from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.api.internal_response import internal_success
from app.schemas.internal_envelope import InternalResponse
from app.schemas.monitor_management import (
    MonitorTargetActionResponse,
    MonitorTargetsListResponse,
)
from app.schemas.monitor_internal import AddByUrlRequest, AddFromCandidatesRequest, AddTargetsResponse
from app.services.monitor_management_service import MonitorManagementService
from app.services.monitor_target_service import MonitorTargetService

router = APIRouter(prefix="/internal/monitor", tags=["internal-monitor"])
service = MonitorTargetService()
mgmt_service = MonitorManagementService()


@router.post("/add-from-candidates", response_model=AddTargetsResponse)
@router.post("/add-from-candidates", response_model=InternalResponse[AddTargetsResponse])
def add_from_candidates(payload: AddFromCandidatesRequest, db: Session = Depends(get_db)) -> dict:
    try:
        rows = service.add_from_candidates(
            db=db,
            batch_id=payload.batch_id,
            candidate_ids=payload.candidate_ids,
            source_type=payload.source_type,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    data = AddTargetsResponse(count=len(rows), targets=rows)
    return internal_success(data)


@router.post("/add-by-url", response_model=AddTargetsResponse)
@router.post("/add-by-url", response_model=InternalResponse[AddTargetsResponse])
def add_by_url(payload: AddByUrlRequest, db: Session = Depends(get_db)) -> dict:
    try:
        row = service.add_by_url(
            db=db,
            url=payload.url,
            source_type=payload.source_type,
            product_name_hint=payload.product_name_hint,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    data = AddTargetsResponse(count=1, targets=[row])
    return internal_success(data)


@router.get("/targets", response_model=InternalResponse[MonitorTargetsListResponse])
def list_targets(
    include_inactive: bool = Query(default=True),
    db: Session = Depends(get_db),
) -> InternalResponse[MonitorTargetsListResponse]:
    data = MonitorTargetsListResponse(**mgmt_service.list_targets(db=db, include_inactive=include_inactive))
    return internal_success(data)


@router.post("/{product_id}/pause", response_model=InternalResponse[MonitorTargetActionResponse])
def pause_target(product_id: int, db: Session = Depends(get_db)) -> dict:
    try:
        data = MonitorTargetActionResponse(**mgmt_service.pause(db=db, product_id=product_id))
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return internal_success(data)


@router.post("/{product_id}/resume", response_model=InternalResponse[MonitorTargetActionResponse])
def resume_target(product_id: int, db: Session = Depends(get_db)) -> dict:
    try:
        data = MonitorTargetActionResponse(**mgmt_service.resume(db=db, product_id=product_id))
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return internal_success(data)


@router.delete("/{product_id}", response_model=InternalResponse[MonitorTargetActionResponse])
def delete_target(product_id: int, db: Session = Depends(get_db)) -> dict:
    try:
        data = MonitorTargetActionResponse(**mgmt_service.delete(db=db, product_id=product_id))
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return internal_success(data)
