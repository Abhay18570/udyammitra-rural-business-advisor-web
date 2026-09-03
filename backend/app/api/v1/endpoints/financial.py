import uuid
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.financial import FinancialAnalysisRequest, FinancialAnalysisResponse
from app.services.financial_service import FinancialService

router = APIRouter()


@router.post("/analyze", response_model=FinancialAnalysisResponse)
def analyze(payload: FinancialAnalysisRequest, user: Annotated[User, Depends(get_current_user)], db: Annotated[Session, Depends(get_db)]) -> FinancialAnalysisResponse:
    return FinancialService(db).analyze(user, payload)


@router.get("/latest", response_model=FinancialAnalysisResponse)
def latest(user: Annotated[User, Depends(get_current_user)], db: Annotated[Session, Depends(get_db)], business_slug: Optional[str] = Query(default=None)) -> FinancialAnalysisResponse:
    return FinancialService(db).latest(user, business_slug)


@router.get("/{analysis_id}", response_model=FinancialAnalysisResponse)
def get_analysis(analysis_id: uuid.UUID, user: Annotated[User, Depends(get_current_user)], db: Annotated[Session, Depends(get_db)]) -> FinancialAnalysisResponse:
    return FinancialService(db).get(user, analysis_id)
