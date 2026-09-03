from datetime import timedelta

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import create_access_token, verify_password
from app.models.user import User

VALID_PASSWORD = "StrongPass1"
REGISTRATION = {"full_name": "Test Entrepreneur", "email": "test@example.com", "mobile_number": "9876543210", "preferred_language": "en", "password": VALID_PASSWORD}


def register(client: TestClient, **overrides: str):
    return client.post("/api/v1/auth/register", json={**REGISTRATION, **overrides})


def test_registration_succeeds_and_password_is_hashed(client: TestClient, db_session: Session) -> None:
    response = register(client)
    assert response.status_code == 201
    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]
    assert body["user"]["role"] == "USER"
    assert "password" not in body["user"] and "password_hash" not in body["user"]
    user = db_session.scalar(select(User).where(User.email == "test@example.com"))
    assert user is not None
    assert user.password_hash != VALID_PASSWORD
    assert verify_password(VALID_PASSWORD, user.password_hash)


def test_duplicate_email_rejected(client: TestClient) -> None:
    assert register(client).status_code == 201
    response = register(client, mobile_number="9876543211")
    assert response.status_code == 409


def test_duplicate_mobile_rejected(client: TestClient) -> None:
    assert register(client).status_code == 201
    response = register(client, email="another@example.com")
    assert response.status_code == 409


def test_login_with_email_succeeds(client: TestClient) -> None:
    register(client)
    response = client.post("/api/v1/auth/login", json={"identifier": "TEST@EXAMPLE.COM", "password": VALID_PASSWORD})
    assert response.status_code == 200
    assert response.json()["user"]["email"] == "test@example.com"


def test_login_with_mobile_succeeds(client: TestClient) -> None:
    register(client)
    response = client.post("/api/v1/auth/login", json={"identifier": "9876543210", "password": VALID_PASSWORD})
    assert response.status_code == 200


def test_wrong_password_rejected(client: TestClient) -> None:
    register(client)
    response = client.post("/api/v1/auth/login", json={"identifier": "test@example.com", "password": "WrongPass1"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email/mobile or password."


def test_me_without_token_rejected(client: TestClient) -> None:
    assert client.get("/api/v1/auth/me").status_code == 401


def test_me_with_valid_token_succeeds(client: TestClient) -> None:
    token = register(client).json()["access_token"]
    response = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["full_name"] == "Test Entrepreneur"


def test_invalid_token_rejected(client: TestClient) -> None:
    response = client.get("/api/v1/auth/me", headers={"Authorization": "Bearer invalid.token.value"})
    assert response.status_code == 401


def test_expired_token_rejected(client: TestClient, db_session: Session) -> None:
    register(client)
    user = db_session.scalar(select(User).where(User.email == "test@example.com"))
    assert user is not None
    token = create_access_token(user, expires_delta=timedelta(seconds=-1))
    response = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Access token has expired."
