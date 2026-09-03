import uuid
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.market import MarketAnalysisRequest, MarketAnalysisResponse, MarketLocationsResponse
from app.services.market_service import MarketService

router = APIRouter()


@router.get("/locations", response_model=MarketLocationsResponse)
def locations(user: Annotated[User, Depends(get_current_user)], db: Annotated[Session, Depends(get_db)]) -> MarketLocationsResponse:
    return MarketService(db).locations(user)


@router.post("/analysis", response_model=MarketAnalysisResponse)
def run_analysis(payload: MarketAnalysisRequest, user: Annotated[User, Depends(get_current_user)], db: Annotated[Session, Depends(get_db)]) -> MarketAnalysisResponse:
    return MarketService(db).run(user, payload)


@router.get("/analyses/latest", response_model=MarketAnalysisResponse)
def latest_analysis(user: Annotated[User, Depends(get_current_user)], db: Annotated[Session, Depends(get_db)]) -> MarketAnalysisResponse:
    return MarketService(db).latest(user)


@router.get("/analyses/{analysis_id}", response_model=MarketAnalysisResponse)
def get_analysis(analysis_id: uuid.UUID, user: Annotated[User, Depends(get_current_user)], db: Annotated[Session, Depends(get_db)]) -> MarketAnalysisResponse:
    return MarketService(db).get(user, analysis_id)
