import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, Float, Integer, String
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class GeocodingCache(Base):
    __tablename__ = "geocoding_cache"
    key: Mapped[str] = mapped_column(String(64), primary_key=True)
    location_fingerprint: Mapped[str] = mapped_column(String(64))
    status: Mapped[str] = mapped_column(String(40))
    result: Mapped[dict] = mapped_column(JSONB)
    fetched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)


class NearbyQueryCache(Base):
    __tablename__ = "nearby_query_cache"
    key: Mapped[str] = mapped_column(String(64), primary_key=True)
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)
    radius_meters: Mapped[int] = mapped_column(Integer)
    provider: Mapped[str] = mapped_column(String(40))
    business_slug: Mapped[str] = mapped_column(String(100))
    mapping_version: Mapped[str] = mapped_column(String(40))
    poi_ids: Mapped[list] = mapped_column(ARRAY(UUID(as_uuid=True)))
    complete: Mapped[bool] = mapped_column(Boolean)
    rejected_record_count: Mapped[int] = mapped_column(Integer)
    fetched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)


class ProviderRequestState(Base):
    __tablename__ = "provider_request_state"
    key: Mapped[str] = mapped_column(String(100), primary_key=True)
    next_allowed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    lease_until: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    lease_owner: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
