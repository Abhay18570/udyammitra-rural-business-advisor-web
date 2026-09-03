import secrets

import pytest

from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.profile import EntrepreneurProfile, EntrepreneurResource, EntrepreneurSkill, ExistingBusiness


def create_user(client: TestClient, marker: str = "one") -> str:
    mobile = "9" + "".join(str(secrets.randbelow(10)) for _ in range(9))
    response = client.post("/api/v1/auth/register", json={"full_name": "Profile User", "email": f"profile-{marker}@example.com", "mobile_number": mobile, "preferred_language": "en", "password": "StrongPass1"})
    assert response.status_code == 201
    return response.json()["access_token"]


def headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def complete_payload(existing: bool = False) -> dict:
    payload = {"full_name": "Updated Entrepreneur", "preferred_language": "mr", "age_group": "AGE_26_35", "education": "GRADUATE", "previous_experience": "ONE_TO_THREE_YEARS", "state": "Maharashtra", "district": "Pune", "taluka": "Haveli", "village": "Wagholi", "pincode": "412207", "capital_range": "RANGE_100000_TO_250000", "own_capital": "150000.00", "loan_required": "50000.00", "skills": [{"name": "Retail"}, {"name": "Other", "other_description": "Bookkeeping"}], "resources": [{"name": "Shop"}, {"name": "Internet"}], "has_existing_business": existing, "onboarding_step": 6, "onboarding_completed": True}
    if existing:
        payload["existing_business"] = {"business_name": "Village Store", "business_category": "Retail", "years_operating": 3, "initial_investment": "200000.00", "monthly_revenue": "75000.00", "monthly_expenses": "50000.00", "employee_count": 2, "estimated_monthly_customers": 500, "major_challenges": "Seasonal demand"}
    return payload


def test_profile_creation_retrieval_and_partial_progress(client: TestClient) -> None:
    token = create_user(client)
    assert client.get("/api/v1/profile", headers=headers(token)).status_code == 404
    response = client.put("/api/v1/profile", headers=headers(token), json={"age_group": "AGE_18_25", "onboarding_step": 2, "onboarding_completed": False})
    assert response.status_code == 200
    assert response.json()["onboarding_step"] == 2
    restored = client.get("/api/v1/profile", headers=headers(token)).json()
    assert restored["age_group"] == "AGE_18_25" and restored["onboarding_completed"] is False


@pytest.mark.parametrize("capital_range", [
    "UP_TO_50000",
    "RANGE_50000_TO_100000",
    "RANGE_100000_TO_250000",
    "RANGE_250000_TO_500000",
    "RANGE_500000_TO_1000000",
    "ABOVE_1000000",
])
def test_every_canonical_capital_range_saves_and_reloads(client: TestClient, capital_range: str) -> None:
    token = create_user(client, capital_range.lower())
    response = client.put("/api/v1/profile", headers=headers(token), json={"capital_range": capital_range, "onboarding_step": 3})
    assert response.status_code == 200
    assert response.json()["capital_range"] == capital_range
    assert client.get("/api/v1/profile", headers=headers(token)).json()["capital_range"] == capital_range


def test_legacy_or_unknown_capital_range_is_rejected(client: TestClient) -> None:
    token = create_user(client, "invalid-capital")
    response = client.put("/api/v1/profile", headers=headers(token), json={"capital_range": "100000_TO_300000", "onboarding_step": 3})
    assert response.status_code == 422
    assert response.json()["detail"]


def test_profile_update_synchronizes_user_fields(client: TestClient) -> None:
    token = create_user(client)
    client.put("/api/v1/profile", headers=headers(token), json={"onboarding_step": 1, "onboarding_completed": False})
    response = client.put("/api/v1/profile", headers=headers(token), json={"full_name": "New Name", "preferred_language": "hi", "onboarding_step": 2, "onboarding_completed": False})
    assert response.json()["full_name"] == "New Name"
    me = client.get("/api/v1/auth/me", headers=headers(token)).json()
    assert me["full_name"] == "New Name" and me["preferred_language"] == "hi"


def test_skills_and_resources_persist_relationally(client: TestClient, db_session: Session) -> None:
    skill_count = db_session.scalar(select(func.count()).select_from(EntrepreneurSkill))
    resource_count = db_session.scalar(select(func.count()).select_from(EntrepreneurResource))
    token = create_user(client)
    response = client.put("/api/v1/profile", headers=headers(token), json={"skills": [{"name": "Tailoring"}, {"name": "Other", "other_description": "Design"}], "resources": [{"name": "Machinery"}], "onboarding_step": 6, "onboarding_completed": False})
    assert response.status_code == 200
    assert {item["name"] for item in response.json()["skills"]} == {"Tailoring", "Other"}
    assert db_session.scalar(select(func.count()).select_from(EntrepreneurSkill)) == skill_count + 2
    assert db_session.scalar(select(func.count()).select_from(EntrepreneurResource)) == resource_count + 1


def test_completion_without_existing_business(client: TestClient, db_session: Session) -> None:
    existing_count = db_session.scalar(select(func.count()).select_from(ExistingBusiness))
    token = create_user(client)
    response = client.put("/api/v1/profile", headers=headers(token), json=complete_payload(False))
    assert response.status_code == 200 and response.json()["onboarding_completed"] is True
    assert response.json()["existing_business"] is None
    assert db_session.scalar(select(func.count()).select_from(ExistingBusiness)) == existing_count


def test_existing_business_persists(client: TestClient, db_session: Session) -> None:
    existing_count = db_session.scalar(select(func.count()).select_from(ExistingBusiness))
    token = create_user(client)
    response = client.put("/api/v1/profile", headers=headers(token), json=complete_payload(True))
    assert response.status_code == 200
    assert response.json()["existing_business"]["business_name"] == "Village Store"
    assert db_session.scalar(select(func.count()).select_from(ExistingBusiness)) == existing_count + 1


def test_switching_to_no_business_removes_record(client: TestClient, db_session: Session) -> None:
    existing_count = db_session.scalar(select(func.count()).select_from(ExistingBusiness))
    token = create_user(client)
    client.put("/api/v1/profile", headers=headers(token), json=complete_payload(True))
    response = client.put("/api/v1/profile", headers=headers(token), json=complete_payload(False))
    assert response.status_code == 200 and response.json()["existing_business"] is None
    assert db_session.scalar(select(func.count()).select_from(ExistingBusiness)) == existing_count


def test_invalid_money_and_pincode_rejected(client: TestClient) -> None:
    token = create_user(client)
    negative = client.put("/api/v1/profile", headers=headers(token), json={"own_capital": "-1", "onboarding_step": 3})
    invalid_pin = client.put("/api/v1/profile", headers=headers(token), json={"pincode": "123", "onboarding_step": 2})
    assert negative.status_code == 422 and invalid_pin.status_code == 422


def test_unauthenticated_access_rejected(client: TestClient) -> None:
    assert client.get("/api/v1/profile").status_code == 401
    assert client.put("/api/v1/profile", json={"onboarding_step": 1}).status_code == 401


def test_profile_is_scoped_to_authenticated_user(client: TestClient, db_session: Session) -> None:
    profile_count = db_session.scalar(select(func.count()).select_from(EntrepreneurProfile))
    first = create_user(client, "first")
    second = create_user(client, "second")
    client.put("/api/v1/profile", headers=headers(first), json={"state": "Maharashtra", "onboarding_step": 2})
    assert client.get("/api/v1/profile", headers=headers(second)).status_code == 404
    assert db_session.scalar(select(func.count()).select_from(EntrepreneurProfile)) == profile_count + 1
