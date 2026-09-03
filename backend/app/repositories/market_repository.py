import uuid
from typing import Optional, Type

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.market import DemoAmenity, DemoInstitution, DemoLocalBusiness, DemoLocation, MarketAnalysis


class MarketRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_locations(self):
        return list(self.db.scalars(select(DemoLocation).where(DemoLocation.is_active.is_(True)).order_by(DemoLocation.name)).all())

    def get_location(self, slug: str) -> Optional[DemoLocation]:
        return self.db.scalar(select(DemoLocation).where(DemoLocation.slug == slug, DemoLocation.is_active.is_(True)))

    def nearby(self, model: Type, location: DemoLocation, radius_km: int):
        distance = func.ST_Distance(model.geo_point, location.geo_point) / 1000.0
        query = select(model, distance.label("distance_km")).where(model.is_active.is_(True), func.ST_DWithin(model.geo_point, location.geo_point, radius_km * 1000)).order_by(distance)
        return list(self.db.execute(query).all())

    def matching_businesses(self, location: DemoLocation, business_profile_id: uuid.UUID):
        distance = func.ST_Distance(DemoLocalBusiness.geo_point, location.geo_point) / 1000.0
        query = select(DemoLocalBusiness, distance.label("distance_km")).where(DemoLocalBusiness.is_active.is_(True), DemoLocalBusiness.business_profile_id == business_profile_id, func.ST_DWithin(DemoLocalBusiness.geo_point, location.geo_point, 10000)).order_by(distance)
        return list(self.db.execute(query).all())

    def save_analysis(self, analysis: MarketAnalysis) -> MarketAnalysis:
        self.db.add(analysis)
        self.db.commit()
        self.db.refresh(analysis)
        return analysis

    def latest(self, user_id: uuid.UUID) -> Optional[MarketAnalysis]:
        return self.db.scalar(select(MarketAnalysis).where(MarketAnalysis.user_id == user_id).order_by(MarketAnalysis.created_at.desc(), MarketAnalysis.id.desc()).limit(1))

    def get_owned(self, analysis_id: uuid.UUID, user_id: uuid.UUID) -> Optional[MarketAnalysis]:
        return self.db.scalar(select(MarketAnalysis).where(MarketAnalysis.id == analysis_id, MarketAnalysis.user_id == user_id))
