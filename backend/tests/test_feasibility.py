import secrets

from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.business import BusinessProfile
from app.models.feasibility import BusinessFeasibilityAnalysis


def register(client: TestClient, marker: str) -> str:
    mobile = "9" + "".join(str(secrets.randbelow(10)) for _ in range(9))
    response = client.post("/api/v1/auth/register", json={"full_name": "Feasibility User", "email": f"feasibility-{marker}-{secrets.token_hex(3)}@example.com", "mobile_number": mobile, "preferred_language": "en", "password": "StrongPass1"})
    assert response.status_code == 201
    return response.json()["access_token"]


def auth(token):
    return {"Authorization": f"Bearer {token}"}


def complete_profile(client: TestClient, token: str, skills=None, resources=None, existing=False):
    payload = {"age_group": "AGE_26_35", "education": "GRADUATE", "previous_experience": "ONE_TO_THREE_YEARS", "state": "Maharashtra", "district": "Satara", "taluka": "Karad", "village": "Karad", "pincode": "415110", "capital_range": "RANGE_100000_TO_250000", "own_capital": "150000.00", "loan_required": "50000.00", "skills": [{"name": item} for item in (skills or ["Retail"])], "resources": [{"name": item} for item in (resources or ["Shop", "Internet"])], "has_existing_business": existing, "onboarding_step": 6, "onboarding_completed": True}
    if existing:
        payload["existing_business"] = {"business_name": "Karad Kirana", "business_category": "Kirana / General Store", "years_operating": 2, "initial_investment": "150000", "monthly_revenue": "50000", "monthly_expenses": "35000", "employee_count": 1, "estimated_monthly_customers": 300}
    assert client.put("/api/v1/profile", headers=auth(token), json=payload).status_code == 200


def market(client, token):
    response = client.post("/api/v1/market/analysis", headers=auth(token), json={"radius_km": 5})
    assert response.status_code == 200
    return response.json()


def test_requires_completed_profile_and_market_analysis(client: TestClient) -> None:
    token = register(client, "requirements")
    response = client.post("/api/v1/feasibility/analyze", headers=auth(token), json={})
    assert response.status_code == 409 and response.json()["detail"]["code"] == "profile_required"
    complete_profile(client, token)
    response = client.post("/api/v1/feasibility/analyze", headers=auth(token), json={})
    assert response.status_code == 409 and response.json()["detail"]["code"] == "market_analysis_required"


def test_analysis_persists_all_results_latest_specific_and_immutable(client: TestClient, db_session: Session) -> None:
    token = register(client, "persist")
    complete_profile(client, token)
    saved_market = market(client, token)
    first = client.post("/api/v1/feasibility/analyze", headers=auth(token), json={"market_analysis_id": saved_market["id"]})
    assert first.status_code == 200
    body = first.json()
    assert body["analysis_version"] == "feasibility-v1"
    assert body["market_analysis_id"] == saved_market["id"]
    assert len(body["results"]) == 8 and len(body["top_matches"]) == 3
    assert [row["rank"] for row in body["results"]] == list(range(1, 9))
    assert all(len(row["components"]) == 6 for row in body["results"])
    assert db_session.scalar(select(func.count()).select_from(BusinessFeasibilityAnalysis).where(BusinessFeasibilityAnalysis.id == body["id"])) == 1
    complete_profile(client, token, skills=["Tailoring"], resources=["Machinery"])
    second = client.post("/api/v1/feasibility/analyze", headers=auth(token), json={}).json()
    assert second["id"] != body["id"]
    assert client.get("/api/v1/feasibility/latest", headers=auth(token)).json()["id"] == second["id"]
    restored = client.get(f"/api/v1/feasibility/{body['id']}", headers=auth(token)).json()
    assert restored["results"] == body["results"]


def test_ownership_for_analysis_and_market_snapshot(client: TestClient) -> None:
    owner, other = register(client, "owner"), register(client, "other")
    complete_profile(client, owner); complete_profile(client, other)
    owner_market = market(client, owner)
    analysis = client.post("/api/v1/feasibility/analyze", headers=auth(owner), json={}).json()
    assert client.get(f"/api/v1/feasibility/{analysis['id']}", headers=auth(other)).status_code == 404
    assert client.post("/api/v1/feasibility/analyze", headers=auth(other), json={"market_analysis_id": owner_market["id"]}).status_code == 404


def test_existing_business_marked_but_ranked_normally(client: TestClient) -> None:
    token = register(client, "existing")
    complete_profile(client, token, existing=True); market(client, token)
    results = client.post("/api/v1/feasibility/analyze", headers=auth(token), json={}).json()["results"]
    current = [row for row in results if row["is_current_business"]]
    assert len(current) == 1 and current[0]["business_slug"] == "kirana-general-store"


def test_different_profiles_change_skill_and_financial_components(client: TestClient) -> None:
    retail, tailoring = register(client, "retail-profile"), register(client, "tailoring-profile")
    complete_profile(client, retail, skills=["Retail"], resources=["Shop", "Internet"])
    complete_profile(client, tailoring, skills=["Tailoring"], resources=["Machinery"])
    market(client, retail); market(client, tailoring)
    retail_result = next(row for row in client.post("/api/v1/feasibility/analyze", headers=auth(retail), json={}).json()["results"] if row["business_slug"] == "tailoring-alteration")
    tailoring_result = next(row for row in client.post("/api/v1/feasibility/analyze", headers=auth(tailoring), json={}).json()["results"] if row["business_slug"] == "tailoring-alteration")
    def component(row, code): return next(item["score"] for item in row["components"] if item["code"] == code)
    assert component(retail_result, "SKILL_MATCH") != component(tailoring_result, "SKILL_MATCH")
    assert component(retail_result, "FINANCIAL_FIT") != component(tailoring_result, "FINANCIAL_FIT")


def test_different_market_location_changes_market_components(client: TestClient) -> None:
    first, second = register(client, "karad-location"), register(client, "wai-location")
    complete_profile(client, first); complete_profile(client, second)
    market(client, first)
    second_market = client.post("/api/v1/market/analysis", headers=auth(second), json={"radius_km": 5, "demo_location_slug": "wai-satara"})
    assert second_market.status_code == 200
    first_results = client.post("/api/v1/feasibility/analyze", headers=auth(first), json={}).json()["results"]
    second_results = client.post("/api/v1/feasibility/analyze", headers=auth(second), json={}).json()["results"]
    market_codes = {"LOCAL_DEMAND", "COMPETITION_OPPORTUNITY", "MARKET_ACCESS", "SUPPLY_CHAIN"}
    first_scores = {row["business_slug"]: [(item["code"], item["score"]) for item in row["components"] if item["code"] in market_codes] for row in first_results}
    second_scores = {row["business_slug"]: [(item["code"], item["score"]) for item in row["components"] if item["code"] in market_codes] for row in second_results}
    assert first_scores != second_scores


def test_inactive_business_is_excluded(client: TestClient, db_session: Session) -> None:
    token = register(client, "inactive")
    complete_profile(client, token); market(client, token)
    business = db_session.scalar(select(BusinessProfile).where(BusinessProfile.slug == "flour-mill"))
    business.is_active = False
    db_session.flush()
    results = client.post("/api/v1/feasibility/analyze", headers=auth(token), json={}).json()["results"]
    assert len(results) == 7 and all(row["business_slug"] != "flour-mill" for row in results)
