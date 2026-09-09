from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.scheme import SchemeAnalysisRequest, SchemeAnalysisResponse
from app.services.scheme_service import SchemeService

router = APIRouter()


@router.post("/analyze", response_model=SchemeAnalysisResponse)
def analyze(payload: SchemeAnalysisRequest, user: Annotated[User, Depends(get_current_user)], db: Annotated[Session, Depends(get_db)]) -> SchemeAnalysisResponse:
    return SchemeService(db).analyze(user, payload)


from app.schemas.scheme import SchemeGuidanceResponse
from app.services.scheme_guidance_service import SchemeGuidanceService


@router.get('/guidance', response_model=SchemeGuidanceResponse)
def guidance(user: Annotated[User, Depends(get_current_user)], db: Annotated[Session, Depends(get_db)]) -> SchemeGuidanceResponse:
    return SchemeGuidanceService(db).guidance(user)
