from sqlalchemy import select
from app.models.business_analysis import BusinessAnalysis


class BusinessAnalysisRepository:
    def __init__(self, db):
        self.db = db

    def save(self, row):
        self.db.add(row)
        self.db.commit()
        return row

    def get_owned(self, analysis_id, user_id):
        return self.db.scalar(select(BusinessAnalysis).where(BusinessAnalysis.id == analysis_id, BusinessAnalysis.user_id == user_id))
