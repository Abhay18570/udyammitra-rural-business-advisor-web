import enum
import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional

from geoalchemy2 import Geography
from sqlalchemy import Boolean, CheckConstraint, DateTime, Enum, ForeignKey, Index, Integer, Numeric, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.business import BusinessCategory, BusinessType


def enum_values(values):
    return [item.value for item in values]


class InstitutionType(str, enum.Enum):
    SCHOOL = "SCHOOL"
    COLLEGE = "COLLEGE"
    HOSPITAL = "HOSPITAL"
    PRIMARY_HEALTH_CENTRE = "PRIMARY_HEALTH_CENTRE"
    BANK = "BANK"
    GRAM_PANCHAYAT = "GRAM_PANCHAYAT"
    MARKET = "MARKET"
    BUS_STAND = "BUS_STAND"
    AGRICULTURAL_MARKET = "AGRICULTURAL_MARKET"
    INDUSTRIAL_CLUSTER = "INDUSTRIAL_CLUSTER"


class AmenityType(str, enum.Enum):
    MARKET = "MARKET"
    BUS_STAND = "BUS_STAND"
    MAJOR_ROAD = "MAJOR_ROAD"
    BANK = "BANK"
    WAREHOUSE = "WAREHOUSE"
    COLD_STORAGE = "COLD_STORAGE"
    TRANSPORT_NODE = "TRANSPORT_NODE"
    AGRI_MARKET = "AGRI_MARKET"
    COLLECTION_CENTRE = "COLLECTION_CENTRE"


class DemoLocation(Base):
    __tablename__ = "demo_locations"
    __table_args__ = (UniqueConstraint("slug"), Index("ix_demo_locations_geo_point", "geo_point", postgresql_using="gist"))
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    slug: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    village: Mapped[str] = mapped_column(String(120), nullable=False)
    taluka: Mapped[str] = mapped_column(String(100), nullable=False)
    district: Mapped[str] = mapped_column(String(100), nullable=False)
    state: Mapped[str] = mapped_column(String(100), nullable=False)
    pincode: Mapped[Optional[str]] = mapped_column(String(6))
    latitude: Mapped[Decimal] = mapped_column(Numeric(9, 6), nullable=False)
    longitude: Mapped[Decimal] = mapped_column(Numeric(9, 6), nullable=False)
    geo_point: Mapped[object] = mapped_column(Geography(geometry_type="POINT", srid=4326, spatial_index=False), nullable=False)
    settlement_density_signal: Mapped[int] = mapped_column(Integer, nullable=False)
    agriculture_intensity_signal: Mapped[int] = mapped_column(Integer, nullable=False)
    commercial_activity_signal: Mapped[int] = mapped_column(Integer, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    is_demo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())


class DemoLocalBusiness(Base):
    __tablename__ = "demo_local_businesses"
    __table_args__ = (UniqueConstraint("demo_location_id", "seed_key", name="uq_demo_local_business_seed"), Index("ix_demo_local_businesses_geo_point", "geo_point", postgresql_using="gist"))
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    demo_location_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("demo_locations.id", ondelete="CASCADE"), nullable=False, index=True)
    business_profile_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("business_profiles.id", ondelete="SET NULL"), index=True)
    seed_key: Mapped[str] = mapped_column(String(120), nullable=False)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    category: Mapped[BusinessCategory] = mapped_column(Enum(BusinessCategory, name="demo_market_business_category", native_enum=False, create_constraint=True, values_callable=enum_values), nullable=False)
    business_type: Mapped[BusinessType] = mapped_column(Enum(BusinessType, name="demo_market_business_type", native_enum=False, create_constraint=True, values_callable=enum_values), nullable=False)
    latitude: Mapped[Decimal] = mapped_column(Numeric(9, 6), nullable=False)
    longitude: Mapped[Decimal] = mapped_column(Numeric(9, 6), nullable=False)
    geo_point: Mapped[object] = mapped_column(Geography(geometry_type="POINT", srid=4326, spatial_index=False), nullable=False)
    source_label: Mapped[str] = mapped_column(String(160), nullable=False)
    is_demo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    business_profile = relationship("BusinessProfile")


class DemoInstitution(Base):
    __tablename__ = "demo_institutions"
    __table_args__ = (UniqueConstraint("demo_location_id", "name", name="uq_demo_institution_name"), Index("ix_demo_institutions_geo_point", "geo_point", postgresql_using="gist"))
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    demo_location_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("demo_locations.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    institution_type: Mapped[InstitutionType] = mapped_column(Enum(InstitutionType, name="institution_type", native_enum=False, create_constraint=True, values_callable=enum_values), nullable=False)
    latitude: Mapped[Decimal] = mapped_column(Numeric(9, 6), nullable=False)
    longitude: Mapped[Decimal] = mapped_column(Numeric(9, 6), nullable=False)
    geo_point: Mapped[object] = mapped_column(Geography(geometry_type="POINT", srid=4326, spatial_index=False), nullable=False)
    is_demo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


class DemoAmenity(Base):
    __tablename__ = "demo_amenities"
    __table_args__ = (UniqueConstraint("demo_location_id", "name", name="uq_demo_amenity_name"), Index("ix_demo_amenities_geo_point", "geo_point", postgresql_using="gist"))
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    demo_location_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("demo_locations.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    amenity_type: Mapped[AmenityType] = mapped_column(Enum(AmenityType, name="amenity_type", native_enum=False, create_constraint=True, values_callable=enum_values), nullable=False)
    latitude: Mapped[Decimal] = mapped_column(Numeric(9, 6), nullable=False)
    longitude: Mapped[Decimal] = mapped_column(Numeric(9, 6), nullable=False)
    geo_point: Mapped[object] = mapped_column(Geography(geometry_type="POINT", srid=4326, spatial_index=False), nullable=False)
    is_demo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


class MarketAnalysis(Base):
    __tablename__ = "market_analyses"
    __table_args__ = (CheckConstraint("analysis_radius_km IN (5, 10)", name="ck_market_analysis_radius"),)
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    demo_location_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("demo_locations.id"), nullable=False, index=True)
    profile_location_snapshot: Mapped[dict] = mapped_column(JSONB, nullable=False)
    analysis_radius_km: Mapped[int] = mapped_column(Integer, nullable=False)
    analysis_version: Mapped[str] = mapped_column(String(30), nullable=False)
    data_version: Mapped[str] = mapped_column(String(40), nullable=False)
    result_snapshot: Mapped[dict] = mapped_column(JSONB, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), index=True)
