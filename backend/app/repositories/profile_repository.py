from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.profile import EntrepreneurProfile
from app.models.user import User


class ProfileRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_for_user(self, user: User) -> Optional[EntrepreneurProfile]:
        return self.db.scalar(select(EntrepreneurProfile).where(EntrepreneurProfile.user_id == user.id))

    def create_for_user(self, user: User) -> EntrepreneurProfile:
        profile = EntrepreneurProfile(user_id=user.id)
        self.db.add(profile)
        self.db.flush()
        return profile

    def save(self, profile: EntrepreneurProfile) -> EntrepreneurProfile:
        self.db.commit()
        self.db.refresh(profile)
        return profile
