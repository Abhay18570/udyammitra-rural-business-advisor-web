from typing import Annotated, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import ExpiredSignatureError, InvalidTokenError
from sqlalchemy.orm import Session

from app.core.security import decode_access_token, token_subject
from app.db.session import get_db
from app.models.user import User, UserRole
from app.repositories.user_repository import UserRepository

bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(credentials: Annotated[Optional[HTTPAuthorizationCredentials], Depends(bearer_scheme)], db: Annotated[Session, Depends(get_db)]) -> User:
    error = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate authentication credentials.", headers={"WWW-Authenticate": "Bearer"})
    if not credentials or credentials.scheme.lower() != "bearer":
        raise error
    try:
        user_id = token_subject(decode_access_token(credentials.credentials))
    except ExpiredSignatureError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Access token has expired.", headers={"WWW-Authenticate": "Bearer"}) from exc
    except InvalidTokenError as exc:
        raise error from exc
    user = UserRepository(db).get_by_id(user_id)
    if not user or not user.is_active:
        raise error
    return user


def require_admin(user: Annotated[User, Depends(get_current_user)]) -> User:
    if user.role not in (UserRole.ADMIN, UserRole.SUPER_ADMIN):
        raise HTTPException(status_code=403, detail="You do not have permission to access the administration portal.")
    return user
