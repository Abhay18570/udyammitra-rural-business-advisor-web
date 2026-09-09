import uuid
from typing import Annotated
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.dependencies import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.business_analysis import BusinessAnalysisRequest, BusinessAnalysisResponse
from app.services.business_analysis_service import BusinessAnalysisService
router = APIRouter()


@router.post('', response_model=BusinessAnalysisResponse, status_code=201)
def analyze(payload: BusinessAnalysisRequest, user: Annotated[User, Depends(get_current_user)], db: Annotated[Session, Depends(get_db)]):
    return BusinessAnalysisService(db).analyze(user, payload)


@router.get('/{analysis_id}', response_model=BusinessAnalysisResponse)
def get_analysis(analysis_id: uuid.UUID, user: Annotated[User, Depends(get_current_user)], db: Annotated[Session, Depends(get_db)]):
    return BusinessAnalysisService(db).get(user, analysis_id)
