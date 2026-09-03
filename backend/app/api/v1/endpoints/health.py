from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from typing import Union

from app.core.config import get_settings
from app.db.session import get_db
from app.schemas.health import DatabaseHealthResponse, HealthResponse

router = APIRouter()


@router.get("", response_model=HealthResponse)
def health() -> HealthResponse:
    settings = get_settings()
    return HealthResponse(status="ok", service=settings.app_name)


@router.get("/database", response_model=DatabaseHealthResponse, responses={503: {"model": DatabaseHealthResponse}})
def database_health(db: Session = Depends(get_db)) -> Union[DatabaseHealthResponse, JSONResponse]:
    try:
        db.execute(text("SELECT 1"))
    except SQLAlchemyError:
        return JSONResponse(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, content={"status": "unavailable", "database": "postgresql"})
    return DatabaseHealthResponse(status="ok", database="postgresql")
