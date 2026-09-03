import uuid
from typing import Optional

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models.user import User


class UserRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, user_id: uuid.UUID) -> Optional[User]:
        return self.db.get(User, user_id)

    def get_by_email(self, email: str) -> Optional[User]:
        return self.db.scalar(select(User).where(User.email == email))

    def get_by_mobile(self, mobile: str) -> Optional[User]:
        return self.db.scalar(select(User).where(User.mobile_number == mobile))

    def get_by_identifier(self, identifier: str) -> Optional[User]:
        normalized = identifier.strip().lower()
        return self.db.scalar(select(User).where(or_(User.email == normalized, User.mobile_number == normalized)))

    def create(self, user: User) -> User:
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
