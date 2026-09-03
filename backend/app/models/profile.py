import enum
import uuid
from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


def enum_values(values):
    return [item.value for item in values]


class AgeGroup(str, enum.Enum):
    AGE_18_25 = "AGE_18_25"
    AGE_26_35 = "AGE_26_35"
    AGE_36_45 = "AGE_36_45"
    AGE_46_60 = "AGE_46_60"
    AGE_60_PLUS = "AGE_60_PLUS"


class EducationLevel(str, enum.Enum):
    NO_FORMAL = "NO_FORMAL"
    UP_TO_10TH = "UP_TO_10TH"
    TWELFTH = "TWELFTH"
    ITI_VOCATIONAL = "ITI_VOCATIONAL"
    DIPLOMA = "DIPLOMA"
    GRADUATE = "GRADUATE"
    POSTGRADUATE = "POSTGRADUATE"
    OTHER = "OTHER"


class ExperienceLevel(str, enum.Enum):
    NONE = "NONE"
    LESS_THAN_1_YEAR = "LESS_THAN_1_YEAR"
    ONE_TO_THREE_YEARS = "ONE_TO_THREE_YEARS"
    THREE_TO_FIVE_YEARS = "THREE_TO_FIVE_YEARS"
    FIVE_PLUS_YEARS = "FIVE_PLUS_YEARS"


class CapitalRange(str, enum.Enum):
    UP_TO_50000 = "UP_TO_50000"
    RANGE_50000_TO_100000 = "RANGE_50000_TO_100000"
    RANGE_100000_TO_250000 = "RANGE_100000_TO_250000"
    RANGE_250000_TO_500000 = "RANGE_250000_TO_500000"
    RANGE_500000_TO_1000000 = "RANGE_500000_TO_1000000"
    ABOVE_1000000 = "ABOVE_1000000"


class EntrepreneurProfile(Base):
    __tablename__ = "entrepreneur_profiles"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    age_group: Mapped[Optional[AgeGroup]] = mapped_column(Enum(AgeGroup, name="age_group", native_enum=False, create_constraint=True, values_callable=enum_values))
    education: Mapped[Optional[EducationLevel]] = mapped_column(Enum(EducationLevel, name="education_level", native_enum=False, create_constraint=True, values_callable=enum_values))
    previous_experience: Mapped[Optional[ExperienceLevel]] = mapped_column(Enum(ExperienceLevel, name="experience_level", native_enum=False, create_constraint=True, values_callable=enum_values))
    state: Mapped[Optional[str]] = mapped_column(String(100))
    district: Mapped[Optional[str]] = mapped_column(String(100))
    taluka: Mapped[Optional[str]] = mapped_column(String(100))
    village: Mapped[Optional[str]] = mapped_column(String(120))
    pincode: Mapped[Optional[str]] = mapped_column(String(6))
    latitude: Mapped[Optional[Decimal]] = mapped_column(Numeric(9, 6))
    longitude: Mapped[Optional[Decimal]] = mapped_column(Numeric(9, 6))
    capital_range: Mapped[Optional[CapitalRange]] = mapped_column(Enum(CapitalRange, name="capital_range", native_enum=False, create_constraint=True, values_callable=enum_values))
    own_capital: Mapped[Optional[Decimal]] = mapped_column(Numeric(14, 2))
    loan_required: Mapped[Optional[Decimal]] = mapped_column(Numeric(14, 2))
    has_existing_business: Mapped[Optional[bool]] = mapped_column(Boolean)
    onboarding_completed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    onboarding_step: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    skills: Mapped[List["EntrepreneurSkill"]] = relationship(cascade="all, delete-orphan", lazy="selectin")
    resources: Mapped[List["EntrepreneurResource"]] = relationship(cascade="all, delete-orphan", lazy="selectin")
    existing_business: Mapped[Optional["ExistingBusiness"]] = relationship(cascade="all, delete-orphan", lazy="selectin", uselist=False)


class EntrepreneurSkill(Base):
    __tablename__ = "entrepreneur_skills"
    __table_args__ = (UniqueConstraint("profile_id", "name", name="uq_entrepreneur_skill"),)
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    profile_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("entrepreneur_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    other_description: Mapped[Optional[str]] = mapped_column(String(120))


class EntrepreneurResource(Base):
    __tablename__ = "entrepreneur_resources"
    __table_args__ = (UniqueConstraint("profile_id", "name", name="uq_entrepreneur_resource"),)
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    profile_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("entrepreneur_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    other_description: Mapped[Optional[str]] = mapped_column(String(120))


class ExistingBusiness(Base):
    __tablename__ = "existing_businesses"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    entrepreneur_profile_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("entrepreneur_profiles.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    business_name: Mapped[str] = mapped_column(String(160), nullable=False)
    business_category: Mapped[str] = mapped_column(String(120), nullable=False)
    years_operating: Mapped[int] = mapped_column(Integer, nullable=False)
    initial_investment: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    monthly_revenue: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    monthly_expenses: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    employee_count: Mapped[int] = mapped_column(Integer, nullable=False)
    estimated_monthly_customers: Mapped[int] = mapped_column(Integer, nullable=False)
    major_challenges: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
