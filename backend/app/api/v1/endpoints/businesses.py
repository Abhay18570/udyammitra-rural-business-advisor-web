from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.business import BusinessCategory, BusinessType
from app.schemas.business import BusinessDetail, BusinessListItem
from app.services.business_service import BusinessService

router = APIRouter()


@router.get("", response_model=List[BusinessListItem])
def list_businesses(db: Annotated[Session, Depends(get_db)], category: Optional[BusinessCategory] = None, business_type: Optional[BusinessType] = None, search: Annotated[Optional[str], Query(max_length=100)] = None) -> List[BusinessListItem]:
    return BusinessService(db).list(category, business_type, search)


@router.get("/{business_id_or_slug}", response_model=BusinessDetail)
def get_business(business_id_or_slug: str, db: Annotated[Session, Depends(get_db)]) -> BusinessDetail:
    return BusinessService(db).get(business_id_or_slug)
