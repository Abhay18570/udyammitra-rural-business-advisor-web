import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.feasibility import BusinessFeasibilityAnalysis


class FeasibilityRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def save(self, analysis: BusinessFeasibilityAnalysis) -> BusinessFeasibilityAnalysis:
        self.db.add(analysis)
        self.db.commit()
        self.db.refresh(analysis)
        return analysis

    def latest(self, user_id: uuid.UUID) -> Optional[BusinessFeasibilityAnalysis]:
        return self.db.scalar(select(BusinessFeasibilityAnalysis).where(BusinessFeasibilityAnalysis.user_id == user_id).order_by(BusinessFeasibilityAnalysis.created_at.desc(), BusinessFeasibilityAnalysis.id.desc()).limit(1))

    def get_owned(self, analysis_id: uuid.UUID, user_id: uuid.UUID) -> Optional[BusinessFeasibilityAnalysis]:
        return self.db.scalar(select(BusinessFeasibilityAnalysis).where(BusinessFeasibilityAnalysis.id == analysis_id, BusinessFeasibilityAnalysis.user_id == user_id))
