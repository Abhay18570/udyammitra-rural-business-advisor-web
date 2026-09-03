from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.business import BusinessCategory, BusinessType
from app.repositories.business_repository import BusinessRepository
from app.schemas.business import BusinessDetail, BusinessListItem


class BusinessService:
    def __init__(self, db: Session) -> None:
        self.businesses = BusinessRepository(db)

    def list(self, category: Optional[BusinessCategory], business_type: Optional[BusinessType], search: Optional[str]) -> List[BusinessListItem]:
        return [BusinessListItem.model_validate(item) for item in self.businesses.list_active(category, business_type, search)]

    def get(self, identifier: str) -> BusinessDetail:
        business = self.businesses.get_active(identifier)
        if not business:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Business profile not found.")
        return BusinessDetail.model_validate(business)
