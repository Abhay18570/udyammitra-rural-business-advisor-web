import enum
import uuid
from datetime import datetime
from decimal import Decimal
from typing import List

from sqlalchemy import Boolean, DateTime, Enum, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


def enum_values(values):
    return [item.value for item in values]


class BusinessCategory(str, enum.Enum):
    RETAIL = "RETAIL"
    SERVICES = "SERVICES"
    AGRICULTURE = "AGRICULTURE"
    FOOD_PROCESSING = "FOOD_PROCESSING"
    MANUFACTURING = "MANUFACTURING"


class BusinessType(str, enum.Enum):
    SERVICE = "SERVICE"
    RETAIL = "RETAIL"
    AGRI_ALLIED = "AGRI_ALLIED"
    PROCESSING = "PROCESSING"
    RENTAL = "RENTAL"


class BusinessProfile(Base):
    __tablename__ = "business_profiles"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    slug: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    name: Mapped[str] = mapped_column(String(160), nullable=False, index=True)
    category: Mapped[BusinessCategory] = mapped_column(Enum(BusinessCategory, name="business_category", native_enum=False, create_constraint=True, values_callable=enum_values), nullable=False, index=True)
    short_description: Mapped[str] = mapped_column(String(320), nullable=False)
    detailed_description: Mapped[str] = mapped_column(Text, nullable=False)
    business_type: Mapped[BusinessType] = mapped_column(Enum(BusinessType, name="business_type", native_enum=False, create_constraint=True, values_callable=enum_values), nullable=False, index=True)
    minimum_capital: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    maximum_capital: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    estimated_setup_cost_min: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    estimated_setup_cost_max: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    working_capital_min: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    working_capital_max: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    required_skills: Mapped[List[str]] = mapped_column(JSONB, nullable=False)
    preferred_skills: Mapped[List[str]] = mapped_column(JSONB, nullable=False)
    required_resources: Mapped[List[str]] = mapped_column(JSONB, nullable=False)
    optional_resources: Mapped[List[str]] = mapped_column(JSONB, nullable=False)
    equipment: Mapped[List[str]] = mapped_column(JSONB, nullable=False)
    customer_segments: Mapped[List[str]] = mapped_column(JSONB, nullable=False)
    market_drivers: Mapped[List[str]] = mapped_column(JSONB, nullable=False)
    competition_factors: Mapped[List[str]] = mapped_column(JSONB, nullable=False)
    supply_chain_factors: Mapped[List[str]] = mapped_column(JSONB, nullable=False)
    major_risks: Mapped[List[str]] = mapped_column(JSONB, nullable=False)
    required_registrations: Mapped[List[str]] = mapped_column(JSONB, nullable=False)
    operating_requirements: Mapped[List[str]] = mapped_column(JSONB, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
