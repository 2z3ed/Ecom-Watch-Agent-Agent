from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.internal_response import internal_success
from app.core.db import get_db
from app.schemas.boss_query import ReportsLatestResponse
from app.schemas.internal_envelope import InternalResponse
from app.services.report_query_service import ReportQueryService

router = APIRouter(prefix="/internal/reports", tags=["internal-reports"])
service = ReportQueryService()


@router.get("/latest", response_model=InternalResponse[ReportsLatestResponse])
def latest_report(db: Session = Depends(get_db)) -> dict:
    data = ReportsLatestResponse(**service.get_latest_report(db=db))
    return internal_success(data)
