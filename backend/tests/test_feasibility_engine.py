from decimal import Decimal
from types import SimpleNamespace

import pytest

from app.engines.feasibility_engine import calculate_weighted_score, financial_fit, rank_results, resource_readiness, skill_match
from app.models.profile import CapitalRange


def test_exact_weighted_formula_and_rounding() -> None:
    score, components = calculate_weighted_score({"LOCAL_DEMAND": 80, "COMPETITION_OPPORTUNITY": 70, "SKILL_MATCH": 90, "FINANCIAL_FIT": 60, "MARKET_ACCESS": 75, "SUPPLY_CHAIN": 65})
    assert score == 75
    assert [item["weighted_contribution"] for item in components] == ["20.00", "14.00", "18.00", "9.00", "7.50", "6.50"]


@pytest.mark.parametrize(("user", "required", "preferred", "score"), [
    (["Tailoring", "Retail"], ["Basic stitching", "Customer service"], ["Pattern cutting"], 100),
    (["Tailoring"], ["Basic stitching", "Customer service"], ["Pattern cutting"], 65),
    (["Computer"], ["Livestock care"], ["Fodder planning"], 0),
    (["Retail"], ["Customer service"], [], 100),
    (["  repairing ", "REPAIRING"], ["Mobile repair basics"], ["Electronics troubleshooting"], 100),
])
def test_skill_matching(user, required, preferred, score) -> None:
    result = skill_match(user, required, preferred)
    assert result["skill_match_score"] == score
    assert len(result["matched_required_skills"]) + len(result["missing_required_skills"]) == len(required)


@pytest.mark.parametrize(("user", "required", "optional", "score"), [
    (["Shop", "Internet"], ["Small shop or workspace"], ["Internet access"], 100),
    (["Water"], ["Reliable water", "Electricity"], ["Internet access"], 40),
    ([], ["Reliable water"], ["Internet access"], 0),
    (["Storage Space", " storage space "], ["Dry storage"], [], 100),
])
def test_resource_readiness(user, required, optional, score) -> None:
    assert resource_readiness(user, required, optional)["resource_readiness_score"] == score


def business(requirement="100000"):
    return SimpleNamespace(minimum_capital=Decimal(requirement), estimated_setup_cost_min=Decimal("80000"), working_capital_min=Decimal("20000"))


def test_financial_fit_exact_range_loan_and_large_decimal() -> None:
    exact = SimpleNamespace(own_capital=Decimal("120000"), capital_range=CapitalRange.UP_TO_50000, loan_required=Decimal("0"))
    near = SimpleNamespace(own_capital=Decimal("80000"), capital_range=None, loan_required=Decimal("0"))
    low = SimpleNamespace(own_capital=Decimal("10000"), capital_range=None, loan_required=Decimal("500000"))
    ranged = SimpleNamespace(own_capital=None, capital_range=CapitalRange.RANGE_50000_TO_100000, loan_required=Decimal("0"))
    huge = SimpleNamespace(own_capital=Decimal("999999999999.99"), capital_range=None, loan_required=Decimal("0"))
    assert financial_fit(exact, business(), 100)[0] == 100
    assert financial_fit(near, business(), 100)[0] == 84
    assert financial_fit(low, business(), 0)[0] == 8  # requested loan does not increase fit
    assert financial_fit(ranged, business(), 100)[0] == 80
    assert financial_fit(huge, business("999999999999.99"), 100)[0] == 100


def test_ranking_tie_break_is_score_then_demand_then_skill_then_name() -> None:
    def item(name, total, demand, skill):
        return {"business_name": name, "business_slug": name.lower(), "final_feasibility_score": total, "components": [{"code": "LOCAL_DEMAND", "score": demand}, {"code": "SKILL_MATCH", "score": skill}]}
    ranked = rank_results([item("C", 70, 90, 20), item("A", 70, 90, 40), item("B", 80, 20, 20)])
    assert [row["business_name"] for row in ranked] == ["B", "A", "C"]
    assert [row["rank"] for row in ranked] == [1, 2, 3]
