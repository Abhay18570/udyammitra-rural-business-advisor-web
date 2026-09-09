"""Pure exact-money routing; no I/O or repayment assumptions."""
from dataclasses import asdict
from decimal import Decimal
from typing import Optional

from app.scheme_rules import SCHEMES, SUPPORTED_PROJECT_COST_MAX, SchemeDefinition
from app.utils.money import parse_inr, format_inr


def classify_project(project_cost: Decimal) -> Optional[SchemeDefinition]:
    project = parse_inr(project_cost)
    if project <= 0:
        raise ValueError("Project cost must be positive.")
    return next((scheme for scheme in SCHEMES
                 if scheme.project_cost_min < project <= scheme.project_cost_max), None)


def calculate_coverage(financing_requirement: Decimal, maximum_loan: Decimal) -> dict:
    requirement, cap = parse_inr(financing_requirement), parse_inr(maximum_loan)
    if requirement < 0 or cap <= 0:
        raise ValueError("Financing requirement must be nonnegative and loan cap positive.")
    principal = min(requirement, cap)
    gap = parse_inr(requirement - principal)
    if principal + gap != requirement:
        raise ArithmeticError("Financing coverage invariant failed.")
    return {"indicative_financed_principal": principal, "scheme_financing_gap": gap,
            "fully_covered": gap == 0, "additional_contribution_required": gap}


def explanation(code: str, message: str, **params: Decimal) -> dict:
    return {"code": code, "params": {key: format(parse_inr(value), ".2f") for key, value in params.items()},
            "message": message}


def evaluate_scheme(project_cost: Decimal, beneficiary_contribution: Decimal, financing_requirement: Decimal) -> dict:
    project, contribution, requirement = map(parse_inr, (project_cost, beneficiary_contribution, financing_requirement))
    if contribution <= 0 or requirement < 0 or contribution + requirement != project:
        raise ValueError("Financial structure is inconsistent.")
    scheme = classify_project(project)
    result = {"project_cost": project, "beneficiary_contribution": contribution, "financing_requirement": requirement,
              "scheme": None, "indicative_financed_principal": None, "scheme_financing_gap": None,
              "fully_covered": None, "additional_contribution_required": None, "total_contribution_required": None,
              "eligibility_reasons": [], "warnings": [], "next_steps": []}
    display = lambda value: format_inr(value, include_paise=True)
    if scheme is None:
        result.update(scheme_status="OUT_OF_SUPPORTED_RANGE", eligibility_reasons=[explanation(
            "PROJECT_OUT_OF_SUPPORTED_RANGE",
            f"Your project cost of {display(project)} exceeds the {display(SUPPORTED_PROJECT_COST_MAX)} financing range supported by this SIH prototype.",
            project_cost=project, supported_project_cost_max=SUPPORTED_PROJECT_COST_MAX)], next_steps=[explanation(
                "REVIEW_PROJECT_SCOPE", "Review your project scope or seek financing guidance outside this prototype.")])
        return result
    coverage = calculate_coverage(requirement, scheme.maximum_loan_amount)
    total = parse_inr(contribution + coverage["additional_contribution_required"])
    if total + coverage["indicative_financed_principal"] != project:
        raise ArithmeticError("Project funding invariant failed.")
    result.update(coverage)
    result.update(scheme=asdict(scheme), total_contribution_required=total,
                  scheme_status="ELIGIBLE" if coverage["fully_covered"] else "ELIGIBLE_WITH_GAP")
    result["eligibility_reasons"] = [explanation(
        f"{scheme.type.value}_PROJECT_TIER",
        f"Your project cost of {display(project)} falls in the {scheme.display_name} tier: above {display(scheme.project_cost_min)} and up to {display(scheme.project_cost_max)}, inclusive.",
        project_cost=project, tier_min=scheme.project_cost_min, tier_max=scheme.project_cost_max), explanation(
        "FINANCING_REQUIREMENT", f"The project cost less your original contribution requires {display(requirement)} in financing.",
        project_cost=project, beneficiary_contribution=contribution, financing_requirement=requirement), explanation(
        "SCHEME_LOAN_CAP", f"The maximum loan under this prototype's {scheme.display_name} rules is {display(scheme.maximum_loan_amount)}.",
        maximum_loan_amount=scheme.maximum_loan_amount)]
    if not coverage["fully_covered"]:
        gap = coverage["scheme_financing_gap"]
        result["warnings"].append(explanation(
            "SCHEME_LOAN_CAP_GAP", f"Your financing requirement is {display(requirement)}, but the scheme loan cap is {display(scheme.maximum_loan_amount)}, leaving a shortfall of {display(gap)}.",
            financing_requirement=requirement, maximum_loan_amount=scheme.maximum_loan_amount, gap=gap))
        result["next_steps"].append(explanation(
            "REVIEW_ADDITIONAL_CONTRIBUTION", f"An additional {display(gap)} would bring your total contribution to {display(total)} for the SAME {display(project)} project. This does not increase the project cost or confirm that you have these funds.",
            additional_contribution_required=gap, total_contribution_required=total, project_cost=project))
    result["next_steps"].append(explanation("VERIFY_LENDER_TERMS", "Verify eligibility and terms with the lender before applying. Repayment planning will be available in Module 13."))
    return result
