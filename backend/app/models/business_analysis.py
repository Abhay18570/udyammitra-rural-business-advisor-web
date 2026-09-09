import uuid
from datetime import datetime
from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, String, event, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class BusinessAnalysis(Base):
    __tablename__ = 'business_analyses'
    __table_args__ = (CheckConstraint('selected_radius BETWEEN 1 AND 10', name='ck_business_analysis_radius'),)
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), index=True)
    business_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('business_profiles.id'))
    financial_analysis_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('financial_analyses.id'))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    selected_radius: Mapped[int] = mapped_column(Integer)
    profile_fingerprint: Mapped[str] = mapped_column(String(64))
    location_fingerprint: Mapped[str] = mapped_column(String(64))
    rule_versions: Mapped[dict] = mapped_column(JSONB)
    catalog_hash: Mapped[str] = mapped_column(String(64))
    context_hash: Mapped[str] = mapped_column(String(64))
    evidence_snapshot: Mapped[dict] = mapped_column(JSONB)
    result_snapshot: Mapped[dict] = mapped_column(JSONB)


@event.listens_for(BusinessAnalysis, 'before_update')
def prevent_snapshot_update(mapper, connection, target):
    raise ValueError('Business analysis snapshots are immutable; generate a new analysis.')
