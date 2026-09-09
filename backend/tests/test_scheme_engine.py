from decimal import Decimal

import pytest

from app.engines.financial_engine import calculate_structure
from app.engines.scheme_engine import calculate_coverage, classify_project, evaluate_scheme
from app.scheme_rules import SCHEMES, SchemeType


@pytest.mark.parametrize(("project", "expected"), [
    ("139999.99", SchemeType.MICRO_FINANCE), ("140000.00", SchemeType.MICRO_FINANCE),
    ("140000.01", SchemeType.TERM_LOAN), ("5000000.00", SchemeType.TERM_LOAN),
    ("5000000.01", None),
])
def test_tier_boundaries(project, expected):
    scheme = classify_project(Decimal(project))
    assert (scheme.type if scheme else None) == expected


@pytest.mark.parametrize("cap", ["125000.00", "4500000.00"])
@pytest.mark.parametrize("offset", ["-0.01", "0.00", "0.01"])
def test_cap_boundaries_independent_of_public_flow(cap, offset):
    requirement = Decimal(cap) + Decimal(offset)
    result = calculate_coverage(requirement, Decimal(cap))
    assert result["indicative_financed_principal"] == min(requirement, Decimal(cap))
    assert result["scheme_financing_gap"] == max(Decimal(offset), Decimal("0.00"))
    assert result["fully_covered"] == (Decimal(offset) <= 0)
    assert result["indicative_financed_principal"] + result["scheme_financing_gap"] == requirement


def route_margin(margin):
    structure = calculate_structure(Decimal(margin))
    return evaluate_scheme(structure["feasible_project_cost"], structure["beneficiary_contribution"], structure["indicative_loan_amount"])


def test_exact_micro_boundary_and_explanations():
    result = route_margin("14000.00")
    assert result["scheme"]["type"] == SchemeType.MICRO_FINANCE
    assert result["scheme_status"] == "ELIGIBLE_WITH_GAP"
    assert result["indicative_financed_principal"] == Decimal("125000.00")
    assert result["scheme_financing_gap"] == result["additional_contribution_required"] == Decimal("1000.00")
    assert result["total_contribution_required"] == Decimal("15000.00")
    assert result["project_cost"] == Decimal("140000.00")
    assert [item["code"] for item in result["eligibility_reasons"]] == ["MICRO_FINANCE_PROJECT_TIER", "FINANCING_REQUIREMENT", "SCHEME_LOAN_CAP"]
    assert result["warnings"][0]["code"] == "SCHEME_LOAN_CAP_GAP"
    assert result["warnings"][0]["params"]["gap"] == "1000.00"
    assert "₹1,000.00" in result["warnings"][0]["message"]
    assert "SAME ₹1,40,000.00 project" in result["next_steps"][0]["message"]


@pytest.mark.parametrize(("margin", "status", "gap"), [
    ("0.01", "ELIGIBLE", "0.00"), ("12000", "ELIGIBLE", "0.00"),
    ("13888.88", "ELIGIBLE", "0.00"), ("13888.89", "ELIGIBLE_WITH_GAP", "0.01"),
    ("13999.99", "ELIGIBLE_WITH_GAP", "999.91"), ("14000.01", "ELIGIBLE", "0.00"),
    ("100000", "ELIGIBLE", "0.00"), ("500000", "ELIGIBLE", "0.00"),
])
def test_reachable_structures_and_invariants(margin, status, gap):
    result = route_margin(margin)
    assert result["scheme_status"] == status
    assert result["scheme_financing_gap"] == Decimal(gap)
    assert result["beneficiary_contribution"] + result["financing_requirement"] == result["project_cost"]
    assert result["total_contribution_required"] + result["indicative_financed_principal"] == result["project_cost"]
    assert result == route_margin(margin)


def test_outside_range_has_no_applicable_loan_or_terms():
    result = route_margin("500000.01")
    assert result["scheme_status"] == "OUT_OF_SUPPORTED_RANGE"
    for field in ("scheme", "indicative_financed_principal", "scheme_financing_gap", "fully_covered", "additional_contribution_required", "total_contribution_required"):
        assert result[field] is None
    assert result["eligibility_reasons"][0]["code"] == "PROJECT_OUT_OF_SUPPORTED_RANGE"


def test_canonical_metadata_and_shared_boundary():
    micro, term = SCHEMES
    assert (micro.maximum_loan_amount, micro.annual_interest_rate_percent, micro.tenure_months, micro.moratorium_months) == (Decimal("125000"), Decimal("6.50"), 36, 3)
    assert (term.maximum_loan_amount, term.annual_interest_rate_percent, term.tenure_months, term.moratorium_months) == (Decimal("4500000"), Decimal("8.00"), 84, 6)
    assert micro.project_cost_max == term.project_cost_min == Decimal("140000")
    assert term.project_cost_max == Decimal("5000000")


@pytest.mark.parametrize("value", ["0", "-1", "NaN", "Infinity", "abc", True, 1.1])
def test_invalid_project_rejected(value):
    with pytest.raises(ValueError):
        classify_project(value)


def test_inconsistent_structure_and_invalid_cap_rejected():
    with pytest.raises(ValueError):
        evaluate_scheme(Decimal("140000"), Decimal("14000"), Decimal("125000"))
    with pytest.raises(ValueError):
        calculate_coverage(Decimal("-1"), Decimal("125000"))
    with pytest.raises(ValueError):
        calculate_coverage(Decimal("1"), Decimal("0"))


def test_cap_uses_existing_half_up_rounding():
    assert calculate_coverage(Decimal("125000.005"), Decimal("125000"))["scheme_financing_gap"] == Decimal("0.01")
