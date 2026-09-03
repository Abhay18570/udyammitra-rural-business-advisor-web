import uuid
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.feasibility import FeasibilityRequest, FeasibilityResponse
from app.services.feasibility_service import FeasibilityService

router = APIRouter()


@router.post("/analyze", response_model=FeasibilityResponse)
def analyze(payload: FeasibilityRequest, user: Annotated[User, Depends(get_current_user)], db: Annotated[Session, Depends(get_db)]) -> FeasibilityResponse:
    return FeasibilityService(db).analyze(user, payload)


@router.get("/latest", response_model=FeasibilityResponse)
def latest(user: Annotated[User, Depends(get_current_user)], db: Annotated[Session, Depends(get_db)]) -> FeasibilityResponse:
    return FeasibilityService(db).latest(user)


@router.get("/{analysis_id}", response_model=FeasibilityResponse)
def get_analysis(analysis_id: uuid.UUID, user: Annotated[User, Depends(get_current_user)], db: Annotated[Session, Depends(get_db)]) -> FeasibilityResponse:
    return FeasibilityService(db).get(user, analysis_id)
