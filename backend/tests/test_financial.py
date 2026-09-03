from sqlalchemy import func, select
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient

from app.models.business import BusinessProfile
from app.models.financial import FinancialAnalysis
from tests.test_feasibility import auth, complete_profile, market, register


def analyze(client, token, margin="100000.00", slug="mobile-repair-accessories", feasibility_id=None):
    return client.post("/api/v1/financial/analyze", headers=auth(token), json={"business_slug": slug, "available_margin_capital": margin, "feasibility_analysis_id": feasibility_id})


def test_validation_and_invalid_business(client: TestClient) -> None:
    token = register(client, "financial-validation")
    for value in ["0", "-1", "abc", "1.234", "10000000.01", "NaN", "Infinity", "-Infinity", "sNaN"]:
        assert analyze(client, token, value).status_code == 422
    assert client.post("/api/v1/financial/analyze", headers=auth(token), json={"business_slug": "mobile-repair-accessories", "available_margin_capital": 12345.67}).status_code == 422
    assert analyze(client, token, slug="not-a-business").status_code == 404


def test_official_one_lakh_example(client: TestClient) -> None:
    token = register(client, "financial-100k")
    response = analyze(client, token, "100000.00")
    assert response.status_code == 200
    body = response.json()
    assert body["available_margin_capital"] == "100000.00"
    assert body["beneficiary_contribution"] == "100000.00"
    assert body["beneficiary_contribution_percentage"] == "10.00"
    assert body["feasible_project_cost"] == "1000000.00"
    assert body["indicative_loan_amount"] == "900000.00"
    assert body["indicative_loan_percentage"] == "90.00"
    assert body["warnings"] == []


def test_fourteen_thousand_boundary(client: TestClient) -> None:
    token = register(client, "financial-14k")
    response = analyze(client, token, "14000.00")
    assert response.status_code == 200
    body = response.json()
    assert body["available_margin_capital"] == "14000.00"
    assert body["beneficiary_contribution"] == "14000.00"
    assert body["feasible_project_cost"] == "140000.00"
    assert body["indicative_loan_amount"] == "126000.00"


def test_exact_api_transport_warning_and_cost_alignment(client: TestClient) -> None:
    token = register(client, "financial-exact")
    response = analyze(client, token, "12345.67")
    assert response.status_code == 200
    body = response.json()
    assert body["available_margin_capital"] == body["beneficiary_contribution"] == "12345.67"
    assert body["feasible_project_cost"] == "123456.70"
    assert body["indicative_loan_amount"] == "111111.03"
    assert body["alignment"]["setup_cost_coverage_status"] == "WITHIN_TYPICAL_RANGE"
    assert body["warnings"] == []
    warning = analyze(client, token, "500000.01").json()
    assert warning["warnings"][0]["code"] == "PROJECT_COST_ABOVE_SUPPORTED_SCHEME_RANGE"
    assert warning["feasible_project_cost"] == "5000000.10"
    assert warning["indicative_loan_amount"] == "4500000.09"


def test_persistence_latest_specific_immutable_and_ownership(client: TestClient, db_session: Session) -> None:
    owner, other = register(client, "financial-owner"), register(client, "financial-other")
    first = analyze(client, owner, "14000.00").json()
    second = analyze(client, owner, "100000.00").json()
    assert first["id"] != second["id"]
    assert db_session.scalar(select(func.count()).select_from(FinancialAnalysis).where(FinancialAnalysis.user_id.is_not(None))) >= 2
    assert client.get("/api/v1/financial/latest", headers=auth(owner)).json()["id"] == second["id"]
    assert client.get("/api/v1/financial/latest?business_slug=mobile-repair-accessories", headers=auth(owner)).json()["id"] == second["id"]
    restored = client.get(f"/api/v1/financial/{first['id']}", headers=auth(owner)).json()
    assert restored["feasible_project_cost"] == "140000.00"
    assert client.get(f"/api/v1/financial/{first['id']}", headers=auth(other)).status_code == 404


def test_feasibility_link_ownership(client: TestClient) -> None:
    owner, other = register(client, "financial-feas-owner"), register(client, "financial-feas-other")
    complete_profile(client, owner); market(client, owner)
    feasibility = client.post("/api/v1/feasibility/analyze", headers=auth(owner), json={}).json()
    assert analyze(client, owner, feasibility_id=feasibility["id"]).json()["feasibility_analysis_id"] == feasibility["id"]
    assert analyze(client, other, feasibility_id=feasibility["id"]).status_code == 404


def test_inactive_business_rejected(client: TestClient, db_session: Session) -> None:
    token = register(client, "financial-inactive")
    business = db_session.scalar(select(BusinessProfile).where(BusinessProfile.slug == "mobile-repair-accessories"))
    business.is_active = False; db_session.flush()
    assert analyze(client, token).status_code == 404
