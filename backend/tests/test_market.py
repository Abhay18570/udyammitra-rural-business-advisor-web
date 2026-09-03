import secrets

from fastapi.testclient import TestClient
from sqlalchemy import func, select, text
from sqlalchemy.orm import Session

from app.data.market_seed import seed_market_data
from app.market_config import DEMO_MARKET_DATA_VERSION, MARKET_ANALYSIS_VERSION, competition_scores
from app.models.market import DemoAmenity, DemoInstitution, DemoLocalBusiness, DemoLocation, MarketAnalysis


def user_token(client: TestClient, marker: str) -> str:
    mobile = "9" + "".join(str(secrets.randbelow(10)) for _ in range(9))
    response = client.post("/api/v1/auth/register", json={"full_name": "Market User", "email": "market-{}-{}@example.com".format(marker, secrets.token_hex(4)), "mobile_number": mobile, "preferred_language": "en", "password": "StrongPass1"})
    assert response.status_code == 201
    return response.json()["access_token"]


def auth(token: str):
    return {"Authorization": "Bearer {}".format(token)}


def profile(client: TestClient, token: str, village="Karad", taluka="Karad", district="Satara", state="Maharashtra"):
    response = client.put("/api/v1/profile", headers=auth(token), json={"state": state, "district": district, "taluka": taluka, "village": village, "pincode": "415110", "onboarding_step": 2})
    assert response.status_code == 200


def test_competition_formula_exact_example() -> None:
    intensity, opportunity = competition_scores(2, 3, 4, 0.4)
    assert intensity == 70
    assert opportunity == 30


def test_seed_is_idempotent_and_has_required_dataset_size(db_session: Session) -> None:
    seed_market_data(db_session)
    second = seed_market_data(db_session)
    assert second == {name: {"created": 0, "updated": 0, "unchanged": count} for name, count in {"locations": 5, "businesses": 100, "institutions": 30, "amenities": 40}.items()}
    assert db_session.scalar(select(func.count()).select_from(DemoLocation).where(DemoLocation.is_active.is_(True))) == 5
    for location_id in db_session.scalars(select(DemoLocation.id)).all():
        assert db_session.scalar(select(func.count()).select_from(DemoLocalBusiness).where(DemoLocalBusiness.demo_location_id == location_id)) == 20


def test_spatial_columns_and_gist_indexes_exist(db_session: Session) -> None:
    assert db_session.scalar(text("SELECT PostGIS_Version()"))
    indexes = set(db_session.scalars(text("SELECT indexname FROM pg_indexes WHERE indexname LIKE 'ix_demo_%_geo_point'")))
    assert indexes == {"ix_demo_locations_geo_point", "ix_demo_local_businesses_geo_point", "ix_demo_institutions_geo_point", "ix_demo_amenities_geo_point"}


def test_locations_require_authentication(client: TestClient) -> None:
    assert client.get("/api/v1/market/locations").status_code == 401
    assert client.post("/api/v1/market/analysis", json={"radius_km": 5}).status_code == 401


def test_supported_location_resolves_conservatively(client: TestClient) -> None:
    token = user_token(client, "resolved")
    profile(client, token, village=" karad ", taluka="KARAD")
    response = client.get("/api/v1/market/locations", headers=auth(token))
    assert response.status_code == 200
    assert response.json()["resolved_location_slug"] == "karad-satara"
    assert response.json()["resolution_status"] == "resolved_demo_location"
    assert len(response.json()["locations"]) == 5


def test_unsupported_location_requires_demo_override_and_preserves_profile(client: TestClient) -> None:
    token = user_token(client, "unsupported")
    profile(client, token, "Wagholi", "Haveli", "Pune")
    locations = client.get("/api/v1/market/locations", headers=auth(token)).json()
    assert locations["resolution_status"] == "unsupported_demo_location"
    assert client.post("/api/v1/market/analysis", headers=auth(token), json={"radius_km": 5}).status_code == 422
    analysis = client.post("/api/v1/market/analysis", headers=auth(token), json={"radius_km": 5, "demo_location_slug": "wai-satara"})
    assert analysis.status_code == 200 and analysis.json()["location_source"] == "demo_override"
    saved_profile = client.get("/api/v1/profile", headers=auth(token)).json()
    assert saved_profile["village"] == "Wagholi" and saved_profile["district"] == "Pune"


def test_five_and_ten_km_analysis_are_deterministic_and_bounded(client: TestClient) -> None:
    token = user_token(client, "radii")
    profile(client, token)
    five = client.post("/api/v1/market/analysis", headers=auth(token), json={"radius_km": 5})
    ten = client.post("/api/v1/market/analysis", headers=auth(token), json={"radius_km": 10})
    assert five.status_code == ten.status_code == 200
    assert len(five.json()["businesses"]) == len(ten.json()["businesses"]) == 8
    assert five.json()["summary"]["business_points_considered"] <= ten.json()["summary"]["business_points_considered"]
    for result in ten.json()["businesses"]:
        assert result["competitors_within_10_km"] == result["competitors_0_2_km"] + result["competitors_2_5_km"] + result["competitors_5_10_km"]
        for field in ("competition_intensity", "competition_opportunity_score", "demand_score", "market_reach_score", "market_access_score", "supply_chain_score", "market_opportunity_signal"):
            assert 0 <= result[field] <= 100
        assert result["evidence"] and isinstance(result["localized_threats"], list)
    assert five.json()["data_version"] == DEMO_MARKET_DATA_VERSION
    assert five.json()["analysis_version"] == MARKET_ANALYSIS_VERSION


def test_nearest_competitor_and_postgis_distance(client: TestClient) -> None:
    token = user_token(client, "distance")
    profile(client, token)
    body = client.post("/api/v1/market/analysis", headers=auth(token), json={"radius_km": 10}).json()
    mobile = next(item for item in body["businesses"] if item["business_slug"] == "mobile-repair-accessories")
    assert mobile["nearest_competitor_km"] is not None
    assert mobile["nearest_competitor_km"] == mobile["nearby_competitors"][0]["distance_km"]
    assert 0 < mobile["nearest_competitor_km"] < 1


def test_analysis_persistence_latest_and_ownership(client: TestClient, db_session: Session) -> None:
    owner = user_token(client, "owner")
    other = user_token(client, "other")
    profile(client, owner)
    profile(client, other, "Satara", "Satara")
    created = client.post("/api/v1/market/analysis", headers=auth(owner), json={"radius_km": 5}).json()
    assert db_session.scalar(select(func.count()).select_from(MarketAnalysis).where(MarketAnalysis.id == created["id"])) == 1
    assert client.get("/api/v1/market/analyses/latest", headers=auth(owner)).json()["id"] == created["id"]
    assert client.get("/api/v1/market/analyses/{}".format(created["id"]), headers=auth(owner)).status_code == 200
    assert client.get("/api/v1/market/analyses/{}".format(created["id"]), headers=auth(other)).status_code == 404


def test_invalid_radius_and_unknown_override_are_rejected(client: TestClient) -> None:
    token = user_token(client, "invalid")
    profile(client, token)
    assert client.post("/api/v1/market/analysis", headers=auth(token), json={"radius_km": 50}).status_code == 422
    assert client.post("/api/v1/market/analysis", headers=auth(token), json={"radius_km": 5, "demo_location_slug": "unknown"}).status_code == 404
