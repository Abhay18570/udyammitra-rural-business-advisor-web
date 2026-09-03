from decimal import Decimal

from app.financial_rules import BENEFICIARY_MARGIN_RATE, LOAN_SHARE_RATE, SUPPORTED_PROJECT_COST_MAX
from app.utils.money import parse_inr


def calculate_structure(available_margin_capital: Decimal) -> dict:
    margin = parse_inr(available_margin_capital)
    project_cost = parse_inr(margin / BENEFICIARY_MARGIN_RATE)
    loan = parse_inr(project_cost * LOAN_SHARE_RATE)
    if parse_inr(margin + loan) != project_cost:
        raise ArithmeticError("Financial structure invariant failed.")
    return {"available_margin_capital": margin, "beneficiary_contribution": margin, "feasible_project_cost": project_cost, "indicative_loan_amount": loan}


def align_business_cost(project_cost: Decimal, business) -> dict:
    project = parse_inr(project_cost)
    setup_min = parse_inr(business.estimated_setup_cost_min)
    setup_max = parse_inr(business.estimated_setup_cost_max)
    if project < setup_min:
        coverage = "BELOW_TYPICAL_RANGE"
        ratio = project / setup_min
        readiness = "PARTIALLY_ALIGNED" if ratio >= Decimal("0.75") else "INSUFFICIENT_CAPITAL_STRUCTURE"
        explanation = "Your current margin capital results in a project capacity below the typical estimated setup range."
    elif project <= setup_max:
        coverage, readiness = "WITHIN_TYPICAL_RANGE", "ALIGNED"
        explanation = "Your calculated project capacity is within the typical estimated setup range."
    else:
        coverage, readiness = "ABOVE_TYPICAL_RANGE", "ABOVE_TYPICAL_REQUIREMENT"
        explanation = "Your calculated project capacity is above the current typical estimate for this business. Consider whether a larger-scale configuration is necessary."
    funding_gap = parse_inr(max(Decimal("0"), setup_min - project))
    above_max = parse_inr(max(Decimal("0"), project - setup_max))
    return {
        "setup_cost_coverage_status": coverage,
        "financial_readiness_status": readiness,
        "funding_gap": funding_gap,
        "capacity_above_estimated_max": above_max,
        "comparison_explanation": explanation,
        "working_capital_explanation": "A portion of the total project cost may need to remain available for working capital.",
    }


def calculate_financial_analysis(margin: Decimal, business) -> dict:
    structure = calculate_structure(margin)
    alignment = align_business_cost(structure["feasible_project_cost"], business)
    warnings = []
    if structure["feasible_project_cost"] > SUPPORTED_PROJECT_COST_MAX:
        warnings.append({"code": "PROJECT_COST_ABOVE_SUPPORTED_SCHEME_RANGE", "message": "The calculated project cost exceeds the currently supported financing range for the upcoming scheme-routing module."})
    return {**structure, **alignment, "warnings": warnings}
