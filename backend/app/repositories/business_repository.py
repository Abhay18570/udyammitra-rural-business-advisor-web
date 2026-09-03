import uuid
from typing import List, Optional

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models.business import BusinessCategory, BusinessProfile, BusinessType


class BusinessRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_active(self, category: Optional[BusinessCategory] = None, business_type: Optional[BusinessType] = None, search: Optional[str] = None) -> List[BusinessProfile]:
        query = select(BusinessProfile).where(BusinessProfile.is_active.is_(True))
        if category is not None:
            query = query.where(BusinessProfile.category == category)
        if business_type is not None:
            query = query.where(BusinessProfile.business_type == business_type)
        if search and search.strip():
            term = "%{}%".format(search.strip())
            query = query.where(or_(BusinessProfile.name.ilike(term), BusinessProfile.short_description.ilike(term), BusinessProfile.slug.ilike(term)))
        return list(self.db.scalars(query.order_by(BusinessProfile.name)).all())

    def get_active(self, identifier: str) -> Optional[BusinessProfile]:
        try:
            business_id = uuid.UUID(identifier)
        except ValueError:
            business_id = None
        query = select(BusinessProfile).where(BusinessProfile.is_active.is_(True))
        query = query.where(BusinessProfile.id == business_id) if business_id else query.where(BusinessProfile.slug == identifier)
        return self.db.scalar(query)
