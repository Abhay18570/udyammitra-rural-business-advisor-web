import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Index, Numeric, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class FinancialAnalysis(Base):
    __tablename__ = "financial_analyses"
    __table_args__ = (Index("ix_financial_user_business_created", "user_id", "business_profile_id", "created_at"),)
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    business_profile_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("business_profiles.id"), nullable=False, index=True)
    feasibility_analysis_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("business_feasibility_analyses.id"), index=True)
    available_margin_capital: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    beneficiary_contribution: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    feasible_project_cost: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    indicative_loan_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    funding_gap: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    analysis_version: Mapped[str] = mapped_column(String(30), nullable=False)
    business_cost_snapshot: Mapped[dict] = mapped_column(JSONB, nullable=False)
    result_snapshot: Mapped[dict] = mapped_column(JSONB, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), index=True)
