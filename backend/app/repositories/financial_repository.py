import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.financial import FinancialAnalysis


class FinancialRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def save(self, analysis: FinancialAnalysis) -> FinancialAnalysis:
        self.db.add(analysis); self.db.commit(); self.db.refresh(analysis); return analysis

    def latest(self, user_id: uuid.UUID, business_id: Optional[uuid.UUID] = None) -> Optional[FinancialAnalysis]:
        query = select(FinancialAnalysis).where(FinancialAnalysis.user_id == user_id)
        if business_id: query = query.where(FinancialAnalysis.business_profile_id == business_id)
        return self.db.scalar(query.order_by(FinancialAnalysis.created_at.desc(), FinancialAnalysis.id.desc()).limit(1))

    def get_owned(self, analysis_id: uuid.UUID, user_id: uuid.UUID) -> Optional[FinancialAnalysis]:
        return self.db.scalar(select(FinancialAnalysis).where(FinancialAnalysis.id == analysis_id, FinancialAnalysis.user_id == user_id))
