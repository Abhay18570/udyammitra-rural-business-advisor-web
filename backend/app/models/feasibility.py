import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class BusinessFeasibilityAnalysis(Base):
    __tablename__ = "business_feasibility_analyses"
    __table_args__ = (Index("ix_feasibility_user_created", "user_id", "created_at"),)
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    market_analysis_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("market_analyses.id"), nullable=False, index=True)
    profile_snapshot: Mapped[dict] = mapped_column(JSONB, nullable=False)
    analysis_version: Mapped[str] = mapped_column(String(30), nullable=False)
    market_analysis_version: Mapped[str] = mapped_column(String(30), nullable=False)
    market_data_version: Mapped[str] = mapped_column(String(40), nullable=False)
    results_snapshot: Mapped[dict] = mapped_column(JSONB, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), index=True)
