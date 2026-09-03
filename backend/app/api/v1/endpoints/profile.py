from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.profile import ProfileResponse, ProfileUpdate
from app.services.profile_service import ProfileService

router = APIRouter()


@router.get("", response_model=ProfileResponse)
def get_profile(user: Annotated[User, Depends(get_current_user)], db: Annotated[Session, Depends(get_db)]) -> ProfileResponse:
    return ProfileService(db).get(user)


@router.put("", response_model=ProfileResponse)
def update_profile(payload: ProfileUpdate, user: Annotated[User, Depends(get_current_user)], db: Annotated[Session, Depends(get_db)]) -> ProfileResponse:
    return ProfileService(db).upsert(user, payload)
