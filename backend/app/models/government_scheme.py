"""Independent discovery catalog; no financing or eligibility rules."""
from typing import Optional
import enum
import uuid
from datetime import datetime

from sqlalchemy import Boolean, CheckConstraint, Computed, DateTime, Enum, Index, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, TSVECTOR, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class SchemeLevel(str, enum.Enum):
    CENTRAL = 'CENTRAL'
    STATE = 'STATE'


class VerificationStatus(str, enum.Enum):
    DATASET_ONLY = 'DATASET_ONLY'
    OFFICIAL_SOURCE_LINKED = 'OFFICIAL_SOURCE_LINKED'
    VERIFIED = 'VERIFIED'
    STALE = 'STALE'


SEARCH_EXPRESSION = "to_tsvector('english'::regconfig, scheme_name || ' ' || details || ' ' || eligibility || ' ' || benefits)"


class GovernmentScheme(Base):
    __tablename__ = 'government_schemes'
    __table_args__ = (
        CheckConstraint("source_type = 'DATASET'", name='government_scheme_source_type'),
        CheckConstraint("level = 'STATE' OR state IS NULL", name='government_scheme_central_state'),
        CheckConstraint("jsonb_typeof(categories) = 'array' AND jsonb_typeof(tags) = 'array'", name='government_scheme_lists'),
        Index('ix_government_schemes_categories', 'categories', postgresql_using='gin'),
        Index('ix_government_schemes_tags', 'tags', postgresql_using='gin'),
        Index('ix_government_schemes_search_vector', 'search_vector', postgresql_using='gin'),
    )
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    slug: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    scheme_name: Mapped[str] = mapped_column(String(300), index=True)
    details: Mapped[str] = mapped_column(Text)
    benefits: Mapped[str] = mapped_column(Text)
    eligibility: Mapped[str] = mapped_column(Text)
    application_process: Mapped[Optional[str]] = mapped_column(Text)
    documents_required: Mapped[Optional[str]] = mapped_column(Text)
    level: Mapped[SchemeLevel] = mapped_column(Enum(SchemeLevel, native_enum=False, create_constraint=True, name='government_scheme_level'), index=True)
    state: Mapped[Optional[str]] = mapped_column(String(100), index=True)
    categories: Mapped[list[str]] = mapped_column(JSONB, default=list, server_default='[]')
    tags: Mapped[list[str]] = mapped_column(JSONB, default=list, server_default='[]')
    source_type: Mapped[str] = mapped_column(String(20), default='DATASET', server_default='DATASET')
    source_dataset: Mapped[str] = mapped_column(String(255))
    verification_status: Mapped[VerificationStatus] = mapped_column(Enum(VerificationStatus, native_enum=False, create_constraint=True, name='government_scheme_verification'), default=VerificationStatus.DATASET_ONLY, server_default='DATASET_ONLY', index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default='true', index=True)
    search_vector: Mapped[str] = mapped_column(TSVECTOR, Computed(SEARCH_EXPRESSION, persisted=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
