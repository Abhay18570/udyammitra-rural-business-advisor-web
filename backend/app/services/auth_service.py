from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User, UserRole
from app.repositories.user_repository import UserRepository
from app.schemas.auth import AuthResponse, LoginRequest, RegisterRequest, UserResponse


class AuthService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.users = UserRepository(db)

    def register(self, payload: RegisterRequest) -> AuthResponse:
        if self.users.get_by_email(str(payload.email)):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="An account with this email already exists.")
        if self.users.get_by_mobile(payload.mobile_number):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="An account with this mobile number already exists.")
        user = User(full_name=payload.full_name, email=str(payload.email), mobile_number=payload.mobile_number, password_hash=hash_password(payload.password), preferred_language=payload.preferred_language, role=UserRole.USER, is_active=True)
        try:
            self.users.create(user)
        except IntegrityError as exc:
            self.db.rollback()
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="An account with these details already exists.") from exc
        return self._auth_response(user)

    def login(self, payload: LoginRequest) -> AuthResponse:
        user = self.users.get_by_identifier(payload.identifier)
        if not user or not verify_password(payload.password, user.password_hash):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email/mobile or password.", headers={"WWW-Authenticate": "Bearer"})
        if not user.is_active:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="This account is inactive.", headers={"WWW-Authenticate": "Bearer"})
        return self._auth_response(user)

    @staticmethod
    def _auth_response(user: User) -> AuthResponse:
        return AuthResponse(access_token=create_access_token(user), user=UserResponse.model_validate(user))
