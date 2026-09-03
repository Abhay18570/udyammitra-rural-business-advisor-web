from decimal import Decimal
from types import SimpleNamespace

import pytest

from app.engines.financial_engine import align_business_cost, calculate_structure


@pytest.mark.parametrize(("margin", "project", "loan"), [
    ("100000.00", "1000000.00", "900000.00"),
    ("14000.00", "140000.00", "126000.00"),
    ("12345.67", "123456.70", "111111.03"),
])
def test_official_structure_examples_are_exact(margin, project, loan) -> None:
    result = calculate_structure(Decimal(margin))
    assert result["beneficiary_contribution"] == Decimal(margin)
    assert result["feasible_project_cost"] == Decimal(project)
    assert result["indicative_loan_amount"] == Decimal(loan)
    assert result["beneficiary_contribution"] + result["indicative_loan_amount"] == result["feasible_project_cost"]


@pytest.mark.parametrize(("project", "coverage", "readiness", "gap", "above"), [
    ("50000", "BELOW_TYPICAL_RANGE", "INSUFFICIENT_CAPITAL_STRUCTURE", "50000.00", "0.00"),
    ("100000", "WITHIN_TYPICAL_RANGE", "ALIGNED", "0.00", "0.00"),
    ("150000", "WITHIN_TYPICAL_RANGE", "ALIGNED", "0.00", "0.00"),
    ("200000", "WITHIN_TYPICAL_RANGE", "ALIGNED", "0.00", "0.00"),
    ("250000", "ABOVE_TYPICAL_RANGE", "ABOVE_TYPICAL_REQUIREMENT", "0.00", "50000.00"),
])
def test_business_alignment_boundaries(project, coverage, readiness, gap, above) -> None:
    business = SimpleNamespace(estimated_setup_cost_min=Decimal("100000"), estimated_setup_cost_max=Decimal("200000"))
    result = align_business_cost(Decimal(project), business)
    assert result["setup_cost_coverage_status"] == coverage
    assert result["financial_readiness_status"] == readiness
    assert result["funding_gap"] == Decimal(gap)
    assert result["capacity_above_estimated_max"] == Decimal(above)
