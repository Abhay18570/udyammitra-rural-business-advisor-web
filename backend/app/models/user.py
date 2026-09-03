import enum
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class PreferredLanguage(str, enum.Enum):
    EN = "en"
    MR = "mr"
    HI = "hi"


class UserRole(str, enum.Enum):
    USER = "USER"
    ADMIN = "ADMIN"
    SUPER_ADMIN = "SUPER_ADMIN"


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    full_name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(320), nullable=False, unique=True, index=True)
    mobile_number: Mapped[str] = mapped_column(String(10), nullable=False, unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    preferred_language: Mapped[PreferredLanguage] = mapped_column(Enum(PreferredLanguage, name="preferred_language", native_enum=False, create_constraint=True, values_callable=lambda values: [item.value for item in values]), nullable=False, default=PreferredLanguage.EN)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole, name="user_role", native_enum=False, create_constraint=True, values_callable=lambda values: [item.value for item in values]), nullable=False, default=UserRole.USER)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
