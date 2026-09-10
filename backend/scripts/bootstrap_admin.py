"""Create an administrator from local configuration without changing existing accounts."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError

from app.core.config import Settings
from app.core.security import hash_password
from app.models.user import PreferredLanguage, User, UserRole
from app.repositories.user_repository import UserRepository
from app.schemas.auth import RegisterRequest


class BootstrapError(Exception):
    """Only credential-free messages may be raised here."""


def bootstrap_admin(db, settings: Settings) -> str:
    try:
        if not (settings.bootstrap_admin_email and settings.bootstrap_admin_password
                and settings.bootstrap_admin_password.get_secret_value()
                and settings.bootstrap_admin_mobile):
            raise BootstrapError("Bootstrap admin configuration is incomplete.")
        try:
            payload = RegisterRequest(
                full_name="Local Administrator",
                email=settings.bootstrap_admin_email,
                mobile_number=settings.bootstrap_admin_mobile,
                password=settings.bootstrap_admin_password.get_secret_value(),
                preferred_language=PreferredLanguage.EN,
            )
        except ValidationError:
            raise BootstrapError("Bootstrap admin configuration is invalid.") from None
        users = UserRepository(db)
        existing = users.get_by_email(str(payload.email))
        mobile_owner = users.get_by_mobile(payload.mobile_number)
        if existing and existing.role not in (UserRole.ADMIN, UserRole.SUPER_ADMIN):
            raise BootstrapError("Account exists with a non-admin role.")
        if mobile_owner and (existing is None or mobile_owner.id != existing.id):
            raise BootstrapError("Mobile number belongs to another account.")
        if existing:
            db.commit()
            return "Admin account already exists."
        db.add(User(
            full_name=payload.full_name, email=str(payload.email),
            mobile_number=payload.mobile_number,
            password_hash=hash_password(payload.password),
            preferred_language=payload.preferred_language,
            role=UserRole.ADMIN, is_active=True,
        ))
        db.commit()
        return "Admin account created successfully."
    except IntegrityError:
        db.rollback()
        raise BootstrapError("Account uniqueness conflict; no account was changed.") from None
    except Exception:
        db.rollback()
        raise


def main() -> int:
    try:
        # Load the backend env even when invoked from the project root.
        from sqlalchemy import create_engine
        from sqlalchemy.orm import Session

        settings = Settings(_env_file=Path(__file__).resolve().parents[1] / ".env")
        engine = create_engine(settings.database_url, pool_pre_ping=True, hide_parameters=True)
        try:
            with Session(engine) as db:
                message = bootstrap_admin(db, settings)
        finally:
            engine.dispose()
        print(message)
        return 0
    except BootstrapError as exc:
        print(str(exc))
    except Exception:
        # Validation and database exceptions may contain credentials or SQL parameters.
        print("Bootstrap admin failed. Check configuration and database availability.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
