from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.internal_response import internal_success
from app.core.db import get_db
from app.schemas.boss_query import TodaySummaryResponse
from app.schemas.internal_envelope import InternalResponse
from app.services.summary_service import SummaryService

router = APIRouter(prefix="/internal/summary", tags=["internal-summary"])
service = SummaryService()


@router.get("/today", response_model=InternalResponse[TodaySummaryResponse])
def today_summary(db: Session = Depends(get_db)) -> dict:
    data = TodaySummaryResponse(**service.get_today_summary(db=db))
    return internal_success(data)
