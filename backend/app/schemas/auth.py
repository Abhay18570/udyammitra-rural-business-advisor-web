import re
import uuid
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.models.user import PreferredLanguage, UserRole

PASSWORD_PATTERN = re.compile(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$")
MOBILE_PATTERN = re.compile(r"^[6-9]\d{9}$")


class RegisterRequest(BaseModel):
    full_name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    mobile_number: str
    preferred_language: PreferredLanguage
    password: str = Field(min_length=8, max_length=128)

    @field_validator("full_name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        return " ".join(value.strip().split())

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return value.strip().lower()

    @field_validator("mobile_number")
    @classmethod
    def validate_mobile(cls, value: str) -> str:
        normalized = re.sub(r"\D", "", value.strip())
        if normalized.startswith("91") and len(normalized) == 12:
            normalized = normalized[2:]
        if not MOBILE_PATTERN.fullmatch(normalized):
            raise ValueError("Enter a valid Indian 10-digit mobile number.")
        return normalized

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        if not PASSWORD_PATTERN.fullmatch(value):
            raise ValueError("Password must contain uppercase, lowercase, and numeric characters.")
        return value


class LoginRequest(BaseModel):
    identifier: str = Field(min_length=1, max_length=320)
    password: str = Field(min_length=1, max_length=128)


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    full_name: str
    email: EmailStr
    mobile_number: str
    preferred_language: PreferredLanguage
    role: UserRole
    is_active: bool


class AuthResponse(BaseModel):
    access_token: str
    token_type: Literal["bearer"] = "bearer"
    user: UserResponse
