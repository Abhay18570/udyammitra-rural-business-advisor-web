from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.data.business_seed import seed_businesses
from app.models.business import BusinessProfile
from app.models.profile import ExistingBusiness


def seeded(db_session: Session) -> None:
    seed_businesses(db_session)


def test_business_list_returns_all_eight_active_profiles(client: TestClient, db_session: Session) -> None:
    seeded(db_session)
    response = client.get("/api/v1/businesses")
    assert response.status_code == 200
    assert len(response.json()) == 8
    assert all(item["is_active"] for item in response.json())


def test_business_detail_supports_slug_and_uuid(client: TestClient, db_session: Session) -> None:
    seeded(db_session)
    by_slug = client.get("/api/v1/businesses/mobile-repair-accessories")
    assert by_slug.status_code == 200
    detail = by_slug.json()
    assert detail["name"] == "Mobile Repair & Accessories"
    assert "Mobile repair basics" in detail["required_skills"]
    assert detail["equipment"] and detail["market_drivers"] and detail["required_registrations"]
    by_id = client.get("/api/v1/businesses/{}".format(detail["id"]))
    assert by_id.status_code == 200 and by_id.json()["slug"] == detail["slug"]


def test_inactive_business_is_excluded_from_list_and_detail(client: TestClient, db_session: Session) -> None:
    seeded(db_session)
    business = db_session.scalar(select(BusinessProfile).where(BusinessProfile.slug == "flour-mill"))
    business.is_active = False
    db_session.commit()
    assert len(client.get("/api/v1/businesses").json()) == 7
    assert client.get("/api/v1/businesses/flour-mill").status_code == 404


def test_category_filter(client: TestClient, db_session: Session) -> None:
    seeded(db_session)
    response = client.get("/api/v1/businesses", params={"category": "FOOD_PROCESSING"})
    assert response.status_code == 200
    assert {item["slug"] for item in response.json()} == {"flour-mill", "food-processing-unit"}


def test_business_type_filter(client: TestClient, db_session: Session) -> None:
    seeded(db_session)
    response = client.get("/api/v1/businesses", params={"business_type": "AGRI_ALLIED"})
    assert response.status_code == 200
    assert {item["slug"] for item in response.json()} == {"dairy-enterprise", "poultry-enterprise"}


def test_search_is_case_insensitive(client: TestClient, db_session: Session) -> None:
    seeded(db_session)
    response = client.get("/api/v1/businesses", params={"search": "MOBILE"})
    assert response.status_code == 200
    assert [item["slug"] for item in response.json()] == ["mobile-repair-accessories"]


def test_missing_business_returns_404(client: TestClient, db_session: Session) -> None:
    seeded(db_session)
    response = client.get("/api/v1/businesses/not-a-supported-business")
    assert response.status_code == 404


def test_seed_is_idempotent_and_keeps_user_business_separate(db_session: Session) -> None:
    seed_businesses(db_session)
    second = seed_businesses(db_session)
    assert second["created"] == 0
    assert db_session.scalar(select(func.count()).select_from(BusinessProfile)) == 8
    assert BusinessProfile.__tablename__ != ExistingBusiness.__tablename__
