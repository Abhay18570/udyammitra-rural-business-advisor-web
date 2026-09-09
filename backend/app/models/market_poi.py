import uuid
from datetime import datetime

from geoalchemy2 import Geography
from sqlalchemy import DateTime, Index, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class MarketPOI(Base):
    __tablename__ = "market_pois"
    __table_args__ = (UniqueConstraint("provider", "external_type", "external_id", name="uq_market_poi_external"),
                      Index("ix_market_pois_geo_point", "geo_point", postgresql_using="gist"))
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    provider: Mapped[str] = mapped_column(String(40))
    external_type: Mapped[str] = mapped_column(String(12))
    external_id: Mapped[str] = mapped_column(String(255))
    name: Mapped[str] = mapped_column(String(2000))
    geo_point: Mapped[object] = mapped_column(Geography(geometry_type="POINT", srid=4326, spatial_index=False))
    coordinate_kind: Mapped[str] = mapped_column(String(30))
    normalized_tags: Mapped[dict] = mapped_column(JSONB)
    normalized_address: Mapped[dict] = mapped_column(JSONB)
    fetched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
