import copy
import re
import uuid
from decimal import Decimal

import pytest
from sqlalchemy import event, func, select

from app.models.financial import FinancialAnalysis
from tests.test_financial import analyze
from tests.test_feasibility import auth, register


def route(client, token, analysis_id, **extra):
    return client.post("/api/v1/schemes/analyze", headers=auth(token), json={"financial_analysis_id": analysis_id, **extra})


def test_authentication_and_safe_ownership(client):
    owner, other = register(client, "scheme-owner"), register(client, "scheme-other")
    saved = analyze(client, owner, "14000").json()
    assert client.post("/api/v1/schemes/analyze", json={"financial_analysis_id": saved["id"]}).status_code == 401
    assert route(client, "invalid-token", saved["id"]).status_code == 401
    foreign = route(client, other, saved["id"])
    missing = route(client, other, str(uuid.uuid4()))
    assert foreign.status_code == missing.status_code == 404
    assert foreign.json() == missing.json()


@pytest.mark.parametrize("payload", [{}, {"financial_analysis_id": None}, {"financial_analysis_id": "bad"}, {"financial_analysis_id": 12}, {"financial_analysis_id": True}])
def test_invalid_request(client, payload):
    token = register(client, "scheme-invalid")
    assert client.post("/api/v1/schemes/analyze", headers=auth(token), json=payload).status_code == 422


@pytest.mark.parametrize("field", ["interest_rate", "tenure", "moratorium", "loan_cap", "scheme_type", "project_cost", "calculated_loan_amount", "available_margin_capital"])
def test_forbidden_frontend_financial_fields(client, field):
    token = register(client, "scheme-extra")
    assert route(client, token, str(uuid.uuid4()), **{field: "1"}).status_code == 422


def test_boundary_response_is_exact_and_read_only(client, db_session):
    token = register(client, "scheme-exact")
    saved = analyze(client, token, "14000.00").json()
    stored = db_session.get(FinancialAnalysis, uuid.UUID(saved["id"]))
    snapshot = copy.deepcopy(stored.result_snapshot)
    before = db_session.scalar(select(func.count()).select_from(FinancialAnalysis))
    writes = []
    def capture(_conn, _cursor, statement, _parameters, _context, _executemany):
        if statement.lstrip().split()[0].upper() in {"INSERT", "UPDATE", "DELETE", "CREATE", "ALTER"}:
            writes.append(statement)
    connection = db_session.connection()
    event.listen(connection, "before_cursor_execute", capture)
    try:
        response = route(client, token, saved["id"])
        repeated = route(client, token, saved["id"])
    finally:
        event.remove(connection, "before_cursor_execute", capture)
    assert response.status_code == 200, response.text
    assert response.json() == repeated.json()
    body = response.json()
    assert writes == []
    assert db_session.scalar(select(func.count()).select_from(FinancialAnalysis)) == before
    db_session.refresh(stored)
    assert stored.result_snapshot == snapshot
    assert body["financial_analysis_id"] == saved["id"]
    assert body["financial_analysis_version"] == "financial-v1"
    assert body["scheme_rules_version"] == "scheme-v1"
    assert body["business"] == saved["business"]
    assert body["scheme_status"] == "ELIGIBLE_WITH_GAP"
    assert body["calculation_status"] == "CALCULATED"
    assert body["verification_required"] is True
    assert body["eligibility_basis"] == "PROTOTYPE_FINANCING_RULES"
    assert body["currency"] == "INR"
    assert body["rounding"] == "HALF_UP_TO_PAISE"
    assert body["repayment_basis"] is None
    expected = {"project_cost": "140000.00", "beneficiary_contribution": "14000.00", "financing_requirement": "126000.00", "indicative_financed_principal": "125000.00", "scheme_financing_gap": "1000.00", "additional_contribution_required": "1000.00", "total_contribution_required": "15000.00"}
    for field, value in expected.items():
        assert body[field] == value
        assert re.fullmatch(r"\d+\.\d{2}", body[field])
    assert body["scheme"] == {"type": "MICRO_FINANCE", "display_name": "Micro Finance", "project_cost_min": "0.00", "project_cost_max": "140000.00", "project_cost_min_inclusive": False, "project_cost_max_inclusive": True, "maximum_loan_amount": "125000.00", "annual_interest_rate_percent": "6.50", "tenure_months": 36, "moratorium_months": 3}
    assert body["warnings"][0]["code"] == "SCHEME_LOAN_CAP_GAP"
    assert body["warnings"][0]["params"]["gap"] == "1000.00"


@pytest.mark.parametrize(("margin", "expected_status", "scheme"), [
    ("0.01", "ELIGIBLE", "MICRO_FINANCE"), ("13888.88", "ELIGIBLE", "MICRO_FINANCE"),
    ("13888.89", "ELIGIBLE_WITH_GAP", "MICRO_FINANCE"), ("13999.99", "ELIGIBLE_WITH_GAP", "MICRO_FINANCE"),
    ("14000.01", "ELIGIBLE", "TERM_LOAN"), ("500000", "ELIGIBLE", "TERM_LOAN"),
    ("500000.01", "OUT_OF_SUPPORTED_RANGE", None),
])
def test_public_flow_boundaries(client, margin, expected_status, scheme):
    token = register(client, "scheme-flow")
    saved = analyze(client, token, margin).json()
    response = route(client, token, saved["id"])
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["scheme_status"] == expected_status
    if scheme:
        assert body["scheme"]["type"] == scheme
        if scheme == "TERM_LOAN":
            assert body["scheme"]["maximum_loan_amount"] == "4500000.00"
            assert body["scheme"]["annual_interest_rate_percent"] == "8.00"
            assert body["scheme"]["tenure_months"] == 84
            assert body["scheme"]["moratorium_months"] == 6
    else:
        for field in ("scheme", "indicative_financed_principal", "fully_covered", "scheme_financing_gap", "additional_contribution_required", "total_contribution_required"):
            assert body[field] is None


@pytest.mark.parametrize("field", ["analysis_version", "available_margin_capital", "beneficiary_contribution", "feasible_project_cost", "indicative_loan_amount", "result_snapshot"])
def test_incompatible_snapshot_conflicts(client, db_session, field):
    token = register(client, "scheme-conflict")
    saved = analyze(client, token, "14000").json()
    stored = db_session.get(FinancialAnalysis, uuid.UUID(saved["id"]))
    if field == "analysis_version":
        stored.analysis_version = "financial-v99"
    elif field == "result_snapshot":
        stored.result_snapshot = {"business": {**saved["business"], "id": str(uuid.uuid4())}}
    else:
        setattr(stored, field, getattr(stored, field) + Decimal("0.01"))
    db_session.flush()
    response = route(client, token, saved["id"])
    assert response.status_code == 409
    assert response.json()["detail"]["code"] == ("unsupported_financial_version" if field == "analysis_version" else "inconsistent_financial_snapshot")
